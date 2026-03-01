"""
Central configuration for the Legal AI Demo.
All environment variables are loaded here via pydantic-settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # ── Application ───────────────────────────────────────────────────────────
    APP_NAME: str = "Legal AI Demo"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # ── Gemini (primary – free tier via Google AI Studio) ─────────────────────
    GEMINI_API_KEY: str = ""
    LLM_MODEL: str = "gemini-2.0-flash"      # free-tier Gemini model
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 2048

    # ── RAG / Vector Store ─────────────────────────────────────────────────────
    VECTOR_STORE_DIR: str = str(BASE_DIR / "vector_store")
    EMBED_MODEL: str = "models/text-embedding-004"   # Google embedding model
    RAG_TOP_K: int = 4                       # chunks returned per query
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100

    # ── Document Upload ────────────────────────────────────────────────────────
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".docx", ".txt"]
    MAX_FILE_SIZE_MB: int = 20

    # ── ASR (Speech-to-Text) ──────────────────────────────────────────────────
    # Provider options: "gemini" (free) | "local_whisper" (offline)
    ASR_PROVIDER: str = "gemini"
    ASR_MODEL: str = "gemini-2.0-flash"      # multimodal model used for transcription
    LOCAL_WHISPER_MODEL: str = "base"        # used only when provider=local_whisper

    # ── TTS (Text-to-Speech) ──────────────────────────────────────────────────
    # Provider options: "gemini" (free) | "gtts" (free, lower quality)
    TTS_PROVIDER: str = "gemini"
    TTS_MODEL: str = "gemini-2.5-flash-preview-tts"
    TTS_VOICE: str = "Aoede"                 # see docs for all 30 voices

    # ── Legal Context ──────────────────────────────────────────────────────────
    LEGAL_DOCS_DIR: str = str(BASE_DIR / "data" / "saudi_legal_samples")
    SYSTEM_PROMPT: str = (
        "أنت مساعد قانوني ذكي متخصص في الأنظمة والتشريعات السعودية. "
        "أجب بدقة وأمانة بناءً على المستندات المتاحة. "
        "إذا لم تجد إجابة في السياق، وضّح ذلك بوضوح ولا تخترع معلومات. "
        "الرد باللغة العربية ما لم يطلب المستخدم غير ذلك."
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton of Settings."""
    return Settings()
