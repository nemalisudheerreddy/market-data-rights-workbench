import hashlib
import uuid
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, engine, get_db
from app.llm import answer_question
from app.models import Document
from app.parsers import parse_file
from app.retrieval import search_documents


settings = get_settings()
Base.metadata.create_all(bind=engine)

upload_directory = Path(settings.upload_directory)
upload_directory.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Market Data Rights Workbench API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


@app.get("/api/health")
def health():
    return {"status": "healthy"}


@app.get("/api/documents")
def list_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).order_by(Document.id.desc()).all()

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "sha256": document.sha256,
            "parser_name": document.parser_name,
            "processing_status": document.processing_status,
            "created_at": document.created_at,
        }
        for document in documents
    ]


@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    original_filename = Path(file.filename or "unnamed").name
    extension = Path(original_filename).suffix.lower()

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".csv",
        ".xlsx",
        ".json",
        ".txt",
        ".md",
    }

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}",
        )

    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()

    duplicate = (
        db.query(Document)
        .filter(Document.sha256 == file_hash)
        .first()
    )

    if duplicate:
        return {
            "duplicate": True,
            "document_id": duplicate.id,
            "filename": duplicate.filename,
        }

    stored_filename = f"{uuid.uuid4().hex}{extension}"
    stored_path = upload_directory / stored_filename
    stored_path.write_bytes(content)

    try:
        extracted_text, parser_name = parse_file(stored_path)
    except Exception as error:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(error)) from error

    document = Document(
        filename=original_filename,
        stored_filename=stored_filename,
        file_type=extension.lstrip("."),
        sha256=file_hash,
        parser_name=parser_name,
        processing_status="processed",
        extracted_text=extracted_text,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "duplicate": False,
        "document_id": document.id,
        "filename": document.filename,
        "characters_extracted": len(extracted_text),
    }


@app.post("/api/ask")
async def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db),
):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question is required.",
        )

    documents = db.query(Document).all()
    results = search_documents(question, documents)

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No processed corpus documents are available.",
        )

    answer = await answer_question(question, results)

    return {
        "question": question,
        "answer": answer,
        "retrieved_sources": [
            {
                "document_id": result.document_id,
                "filename": result.filename,
                "score": result.score,
            }
            for result in results
        ],
    }