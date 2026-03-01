"""
API Client – thin wrapper around httpx calls to the FastAPI backend.
All API communication is centralised here so the UI components stay clean.
"""

import httpx
from typing import Any

BACKEND_URL = "http://localhost:8000"
TIMEOUT = 60.0          # seconds – LLM calls can take a while


def _client() -> httpx.Client:
    return httpx.Client(base_url=BACKEND_URL, timeout=TIMEOUT)


def _raise_for_status_with_detail(response: httpx.Response) -> None:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = None
        try:
            payload = response.json()
            detail = payload.get("detail") if isinstance(payload, dict) else None
        except Exception:
            detail = None

        if detail:
            raise RuntimeError(f"{exc}. Detail: {detail}") from exc
        raise


def chat(message: str, history: list[dict], use_rag: bool = True) -> dict:
    payload = {"message": message, "history": history, "use_rag": use_rag}
    with _client() as c:
        r = c.post("/api/chat", json=payload)
        _raise_for_status_with_detail(r)
        return r.json()


def upload_document(file_bytes: bytes, filename: str) -> dict:
    with _client() as c:
        r = c.post(
            "/api/documents/upload",
            files={"file": (filename, file_bytes, "application/octet-stream")},
        )
        _raise_for_status_with_detail(r)
        return r.json()


def list_documents() -> list[dict]:
    with _client() as c:
        r = c.get("/api/documents")
        _raise_for_status_with_detail(r)
        return r.json()


def delete_document(doc_id: str) -> None:
    with _client() as c:
        r = c.delete(f"/api/documents/{doc_id}")
        _raise_for_status_with_detail(r)


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> dict:
    with _client() as c:
        r = c.post(
            "/api/voice/transcribe",
            files={"audio": (filename, audio_bytes, "audio/wav")},
        )
        _raise_for_status_with_detail(r)
        return r.json()


def synthesize_speech(text: str, voice: str | None = None) -> bytes:
    payload: dict[str, Any] = {"text": text}
    if voice:
        payload["voice"] = voice
    with _client() as c:
        r = c.post("/api/voice/synthesize", json=payload)
        _raise_for_status_with_detail(r)
        return r.content


def health_check() -> dict:
    with _client() as c:
        r = c.get("/health")
        _raise_for_status_with_detail(r)
        return r.json()
