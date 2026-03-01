"""
tests/test_documents.py
Tests for document upload, ingestion, listing, and deletion flows.
Run with: pytest tests/
"""

import pytest
import io
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


# ── Health check ─────────────────────────────────────────────────────────────────

def test_health_endpoint():
    """Health endpoint should always return 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "components" in data


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Legal AI Demo" in response.json()["message"]


# ── Document upload ───────────────────────────────────────────────────────────────

def test_upload_unsupported_file_type():
    """Uploading a .png should return 400."""
    response = client.post(
        "/api/documents/upload",
        files={"file": ("test.png", b"fake image bytes", "image/png")},
    )
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"]


def test_upload_valid_txt_file():
    """A small .txt file should be accepted and ingested."""
    txt_content = (
        "نظام العمل السعودي\n"
        "المادة الأولى: يطبق هذا النظام على العمال والأصحاب.\n"
    ).encode("utf-8")

    with patch("backend.api.routes.documents.save_and_ingest") as mock_ingest:
        mock_ingest.return_value = 3      # pretend 3 chunks were created

        response = client.post(
            "/api/documents/upload",
            files={"file": ("نظام_العمل.txt", txt_content, "text/plain")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["chunks_created"] == 3
    assert data["filename"] == "نظام_العمل.txt"


# ── List documents ────────────────────────────────────────────────────────────────

def test_list_documents_returns_list():
    """GET /api/documents should return a list (may be empty)."""
    with patch("backend.api.routes.documents.list_documents", return_value=[]):
        response = client.get("/api/documents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ── Delete document ───────────────────────────────────────────────────────────────

def test_delete_nonexistent_document():
    """Deleting an unknown doc_id should return 404."""
    with patch("backend.api.routes.documents.delete_document", side_effect=KeyError("abc")):
        response = client.delete("/api/documents/abc")
    assert response.status_code == 404


def test_delete_existing_document():
    """Deleting an existing document should return 204."""
    with patch("backend.api.routes.documents.delete_document", return_value=None):
        response = client.delete("/api/documents/some-valid-doc-id")
    assert response.status_code == 204
