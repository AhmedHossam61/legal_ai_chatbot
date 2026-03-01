"""
Pydantic schemas for request/response validation.
Keep all data contracts in one place for easy editing.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# ── Shared ─────────────────────────────────────────────────────────────────────

class SourceChunk(BaseModel):
    content: str
    source: str
    page: Optional[int] = None


# ── Chat ───────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list)
    use_rag: bool = True                     # toggle RAG for testing


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk] = []
    tokens_used: Optional[int] = None


# ── Documents ──────────────────────────────────────────────────────────────────

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class DocumentUploadResponse(BaseModel):
    doc_id: str
    filename: str
    status: DocumentStatus
    chunks_created: Optional[int] = None
    message: str = ""


class DocumentListItem(BaseModel):
    doc_id: str
    filename: str
    status: DocumentStatus
    uploaded_at: str
    chunks: int = 0


# ── Voice ──────────────────────────────────────────────────────────────────────

class TranscriptionResponse(BaseModel):
    text: str
    language: Optional[str] = None
    duration_seconds: Optional[float] = None


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4096)
    voice: Optional[str] = None              # overrides config default


# ── Health ─────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    components: dict[str, str]
