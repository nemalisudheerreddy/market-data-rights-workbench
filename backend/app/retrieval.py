import re
from dataclasses import dataclass

from rank_bm25 import BM25Okapi


@dataclass
class SearchResult:
    document_id: int
    filename: str
    text: str
    score: float


def tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z0-9_-]+\b", text.lower())


def search_documents(question, documents, top_k: int = 5):
    usable_documents = [
        document
        for document in documents
        if document.extracted_text.strip()
    ]

    if not usable_documents:
        return []

    tokenized_documents = [
        tokenize(document.extracted_text)
        for document in usable_documents
    ]

    index = BM25Okapi(tokenized_documents)
    scores = index.get_scores(tokenize(question))

    ranked = sorted(
        zip(usable_documents, scores),
        key=lambda item: item[1],
        reverse=True,
    )[:top_k]

    results = []

    for document, score in ranked:
        results.append(
            SearchResult(
                document_id=document.id,
                filename=document.filename,
                text=document.extracted_text[:8000],
                score=float(score),
            )
        )

    return results