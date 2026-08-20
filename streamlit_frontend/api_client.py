import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH)

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")

DEFAULT_TIMEOUT = 60
UPLOAD_TIMEOUT = 180
QUESTION_TIMEOUT = 180


class WorkbenchAPIError(Exception):
    pass


def _handle_response(response: requests.Response) -> Any:
    try:
        data = response.json()
    except ValueError:
        data = None

    if response.ok:
        return data

    if isinstance(data, dict):
        detail = data.get("detail", data)
    else:
        detail = response.text or "Unknown API error"

    raise WorkbenchAPIError(
        f"API request failed ({response.status_code}): {detail}"
    )


def get_health() -> dict:
    try:
        response = requests.get(
            f"{API_URL}/api/health",
            timeout=DEFAULT_TIMEOUT,
        )
        return _handle_response(response)
    except requests.RequestException as error:
        raise WorkbenchAPIError(
            f"Cannot connect to FastAPI at {API_URL}. "
            "Confirm that the backend is running."
        ) from error


def get_documents() -> list[dict]:
    try:
        response = requests.get(
            f"{API_URL}/api/documents",
            timeout=DEFAULT_TIMEOUT,
        )
        return _handle_response(response)
    except requests.RequestException as error:
        raise WorkbenchAPIError(
            "Could not retrieve the document inventory."
        ) from error


def upload_document(uploaded_file) -> dict:
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "application/octet-stream",
        )
    }

    try:
        response = requests.post(
            f"{API_URL}/api/documents/upload",
            files=files,
            timeout=UPLOAD_TIMEOUT,
        )
        return _handle_response(response)
    except requests.RequestException as error:
        raise WorkbenchAPIError(
            f"Could not upload {uploaded_file.name}."
        ) from error


def ask_question(question: str) -> dict:
    try:
        response = requests.post(
            f"{API_URL}/api/ask",
            json={"question": question},
            timeout=QUESTION_TIMEOUT,
        )
        return _handle_response(response)
    except requests.RequestException as error:
        raise WorkbenchAPIError(
            "The contract-analysis request failed."
        ) from error