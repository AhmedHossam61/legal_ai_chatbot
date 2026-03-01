"""
Documents route – /api/documents

POST   /api/documents/upload   – upload + ingest a legal document
GET    /api/documents          – list all ingested documents
DELETE /api/documents/{doc_id} – remove a document from the vector store
"""

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.core.config import get_settings
from backend.models.schemas import DocumentUploadResponse, DocumentStatus, DocumentListItem
from backend.services.document_service import (
    save_and_ingest,
    list_documents,
    delete_document,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    """
    Upload a PDF, DOCX, or TXT legal document.
    The file is saved to disk and its contents are chunked and embedded in ChromaDB.
    """
    settings = get_settings()

    # ── Validate extension ──────────────────────────────────────────────────
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {suffix!r} not allowed. Accepted: {settings.ALLOWED_EXTENSIONS}",
        )

    # ── Validate size ───────────────────────────────────────────────────────
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File size {size_mb:.1f} MB exceeds limit of {settings.MAX_FILE_SIZE_MB} MB.",
        )

    doc_id = str(uuid.uuid4())

    try:
        chunks = await save_and_ingest(
            file_bytes=contents,
            filename=file.filename or f"{doc_id}{suffix}",
            doc_id=doc_id,
        )
        return DocumentUploadResponse(
            doc_id=doc_id,
            filename=file.filename or "",
            status=DocumentStatus.READY,
            chunks_created=chunks,
            message=f"Document ingested successfully ({chunks} chunks).",
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Document ingestion failed: %s", file.filename)
        raise HTTPException(
            status_code=500,
            detail="Document upload failed due to an unexpected server error.",
        ) from exc


@router.get("", response_model=list[DocumentListItem])
async def get_documents() -> list[DocumentListItem]:
    """Return a list of all documents that have been uploaded and ingested."""
    return list_documents()


@router.delete("/{doc_id}", status_code=204)
async def remove_document(doc_id: str) -> None:
    """Remove a document and its associated embeddings from the vector store."""
    try:
        delete_document(doc_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Document {doc_id!r} not found.")
    except Exception as exc:
        logger.exception("Failed to delete document %s", doc_id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
