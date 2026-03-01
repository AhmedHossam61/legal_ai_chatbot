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

    # ── LLM ───────────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"          # cheap & fast for demo
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 2048

    # ── RAG / Vector Store ─────────────────────────────────────────────────────
    VECTOR_STORE_DIR: str = str(BASE_DIR / "vector_store")
    EMBED_MODEL: str = "text-embedding-3-small"
    RAG_TOP_K: int = 4                       # chunks returned per query
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100

    # ── Document Upload ────────────────────────────────────────────────────────
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".docx", ".txt"]
    MAX_FILE_SIZE_MB: int = 20

    # ── ASR (Speech-to-Text) ──────────────────────────────────────────────────
    ASR_PROVIDER: str = "openai"             # "openai" | "local_whisper"
    ASR_MODEL: str = "whisper-1"
    LOCAL_WHISPER_MODEL: str = "base"        # used only when provider=local_whisper

    # ── TTS (Text-to-Speech) ──────────────────────────────────────────────────
    TTS_PROVIDER: str = "openai"             # "openai" | "gtts"
    TTS_MODEL: str = "tts-1"
    TTS_VOICE: str = "nova"                  # alloy | echo | fable | onyx | nova | shimmer

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
