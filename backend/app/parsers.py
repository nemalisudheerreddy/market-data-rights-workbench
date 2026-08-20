import json
from pathlib import Path

import fitz
import pandas as pd
from docx import Document as WordDocument


def parse_pdf(path: Path) -> str:
    document = fitz.open(path)
    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text")
        pages.append(f"[Page {page_number}]\n{text}")

    return "\n\n".join(pages)


def parse_docx(path: Path) -> str:
    document = WordDocument(path)
    return "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    )


def parse_csv(path: Path) -> str:
    dataframe = pd.read_csv(path)
    return dataframe.fillna("").to_csv(index=False)


def parse_xlsx(path: Path) -> str:
    workbook = pd.ExcelFile(path)
    sections = []

    for sheet_name in workbook.sheet_names:
        dataframe = pd.read_excel(path, sheet_name=sheet_name)
        sections.append(
            f"[Sheet: {sheet_name}]\n"
            f"{dataframe.fillna('').to_csv(index=False)}"
        )

    return "\n\n".join(sections)


def parse_json(path: Path) -> str:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return json.dumps(data, indent=2, ensure_ascii=False)


def parse_file(path: Path) -> tuple[str, str]:
    extension = path.suffix.lower()

    parsers = {
        ".pdf": (parse_pdf, "PyMuPDF"),
        ".docx": (parse_docx, "python-docx"),
        ".csv": (parse_csv, "pandas-csv"),
        ".xlsx": (parse_xlsx, "pandas-excel"),
        ".json": (parse_json, "json"),
    }

    if extension in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore"), "text"

    if extension not in parsers:
        raise ValueError(f"Unsupported file type: {extension}")

    parser_function, parser_name = parsers[extension]
    return parser_function(path), parser_name