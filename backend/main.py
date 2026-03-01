"""
FastAPI application entry-point – Legal AI Demo Backend.

Run with:
    uvicorn backend.main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import get_settings
from backend.api.routes import chat, documents, voice
from backend.models.schemas import HealthResponse

# ── Logging ─────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Startup / Shutdown ──────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    # Ensure required directories exist
    for dir_path in [settings.UPLOAD_DIR, settings.VECTOR_STORE_DIR, settings.LEGAL_DOCS_DIR]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    logger.info("=== Legal AI Demo starting up (model: %s) ===", settings.LLM_MODEL)
    yield
    logger.info("=== Legal AI Demo shutting down ===")


# ── Application ─────────────────────────────────────────────────────────────────
settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "نظام قانوني ذكي – Demo API\n\n"
        "Supports: LLM chat, RAG over legal documents, ASR (voice input), TTS (voice output)."
    ),
    lifespan=lifespan,
)

# ── CORS (allow Streamlit frontend on port 8501) ────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────────────────────
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(voice.router)


# ── Health check ────────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    """Quick liveness probe – returns the status of all core components."""
    components: dict[str, str] = {}

    # Check Gemini key is set (not valid, just present)
    components["gemini_key"] = "configured" if settings.GEMINI_API_KEY else "MISSING"
    components["vector_store"] = "ready" if Path(settings.VECTOR_STORE_DIR).exists() else "not_found"
    components["uploads_dir"] = "ready" if Path(settings.UPLOAD_DIR).exists() else "not_found"
    components["llm_model"] = settings.LLM_MODEL
    components["asr_provider"] = settings.ASR_PROVIDER
    components["tts_provider"] = settings.TTS_PROVIDER

    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        components=components,
    )


@app.get("/", tags=["System"])
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}. Visit /docs for the API."}
