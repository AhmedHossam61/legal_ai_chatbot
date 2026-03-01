"""
Document Service – file I/O, metadata book-keeping, and RAG ingestion.

A lightweight JSON registry (uploads/registry.json) tracks uploaded
documents so we can list and delete them without a full database.
"""

import json
import logging
import asyncio
import re
from datetime import datetime, timezone
from pathlib import Path

from backend.core.config import get_settings
from backend.core.rag_engine import ingest_file
from backend.models.schemas import DocumentListItem, DocumentStatus

logger = logging.getLogger(__name__)

REGISTRY_FILE = Path(get_settings().UPLOAD_DIR) / "registry.json"


# ── Registry helpers ────────────────────────────────────────────────────────────

def _load_registry() -> dict:
    if REGISTRY_FILE.exists():
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    return {}


def _save_registry(data: dict) -> None:
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _safe_filename(filename: str) -> str:
    """Normalize user-supplied file names for cross-platform filesystem safety."""
    base_name = Path(filename).name.strip()
    if not base_name:
        return "uploaded_document"
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", base_name)
    return sanitized.rstrip(". ") or "uploaded_document"


# ── Public API ──────────────────────────────────────────────────────────────────

async def save_and_ingest(file_bytes: bytes, filename: str, doc_id: str) -> int:
    """
    1. Save the uploaded file under uploads/<doc_id>/<filename>.
    2. Run ingestion (embedding + ChromaDB upsert) in a thread pool
       so we don't block the async event loop.
    3. Register the document in the local JSON registry.

    Returns the number of chunks created.
    """
    settings = get_settings()
    dest_dir = Path(settings.UPLOAD_DIR) / doc_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    clean_filename = _safe_filename(filename)
    dest_path = dest_dir / clean_filename
    dest_path.write_bytes(file_bytes)
    logger.info("Saved upload: %s", dest_path)

    # Run CPU-bound ingestion in a thread executor
    loop = asyncio.get_running_loop()
    try:
        chunks = await loop.run_in_executor(None, ingest_file, dest_path)
    except Exception as exc:
        logger.warning("Ingestion failed for %s: %s", clean_filename, exc)
        raise ValueError(f"Unable to process file '{clean_filename}': {exc}") from exc

    # Update registry
    registry = _load_registry()
    registry[doc_id] = {
        "doc_id": doc_id,
        "filename": clean_filename,
        "status": DocumentStatus.READY.value,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "chunks": chunks,
        "file_path": str(dest_path),
    }
    _save_registry(registry)

    return chunks


def list_documents() -> list[DocumentListItem]:
    """Return all registered documents."""
    registry = _load_registry()
    return [
        DocumentListItem(
            doc_id=entry["doc_id"],
            filename=entry["filename"],
            status=DocumentStatus(entry["status"]),
            uploaded_at=entry["uploaded_at"],
            chunks=entry.get("chunks", 0),
        )
        for entry in registry.values()
    ]


def delete_document(doc_id: str) -> None:
    """
    Remove a document's embeddings from ChromaDB and delete it from disk + registry.
    Raises KeyError if doc_id is not found.
    """
    registry = _load_registry()
    if doc_id not in registry:
        raise KeyError(doc_id)

    entry = registry.pop(doc_id)

    # Remove file from disk
    file_path = Path(entry.get("file_path", ""))
    if file_path.exists():
        file_path.unlink()
        try:
            file_path.parent.rmdir()   # remove folder if empty
        except OSError:
            pass

    # Remove embeddings from ChromaDB
    try:
        from langchain_chroma import Chroma
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from backend.core.config import get_settings

        settings = get_settings()
        embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.EMBED_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
        )
        vs = Chroma(
            persist_directory=settings.VECTOR_STORE_DIR,
            embedding_function=embeddings,
            collection_name="legal_docs",
        )
        # Delete all chunks whose metadata.doc_id matches
        existing = vs.get(where={"doc_id": doc_id})
        if existing and existing.get("ids"):
            vs.delete(ids=existing["ids"])
            logger.info("Removed %d vectors for doc_id=%s", len(existing["ids"]), doc_id)
    except Exception as exc:
        logger.warning("Could not remove vectors for %s: %s", doc_id, exc)

    _save_registry(registry)
    logger.info("Document %s deleted", doc_id)
