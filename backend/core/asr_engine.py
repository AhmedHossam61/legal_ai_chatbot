"""
ASR Engine – Speech-to-Text.

Supports two providers (set ASR_PROVIDER in .env):
  • "openai"         – OpenAI Whisper API  (requires API key, no local GPU needed)
  • "local_whisper"  – openai-whisper library running locally (offline, slower)
"""

import logging
import tempfile
from pathlib import Path

from backend.core.config import get_settings

logger = logging.getLogger(__name__)


async def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> dict:
    """
    Transcribe audio bytes and return:
      {"text": str, "language": str | None, "duration_seconds": float | None}

    Parameters
    ----------
    audio_bytes : bytes  – Raw audio data (webm, wav, mp3, m4a, …)
    filename    : str    – Original filename (used to infer mime type)
    """
    settings = get_settings()
    provider = settings.ASR_PROVIDER.lower()

    if provider == "openai":
        return await _transcribe_openai(audio_bytes, filename, settings)
    elif provider == "local_whisper":
        return _transcribe_local(audio_bytes, settings)
    else:
        raise ValueError(f"Unknown ASR_PROVIDER: {provider!r}. Use 'openai' or 'local_whisper'.")


# ── OpenAI Whisper API ──────────────────────────────────────────────────────────

async def _transcribe_openai(audio_bytes: bytes, filename: str, settings) -> dict:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # The API requires a file-like object with a name attribute
    import io
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename

    logger.debug("Calling OpenAI Whisper API, model=%s", settings.ASR_MODEL)
    response = await client.audio.transcriptions.create(
        model=settings.ASR_MODEL,
        file=audio_file,
        response_format="verbose_json",
    )

    return {
        "text": response.text,
        "language": getattr(response, "language", None),
        "duration_seconds": getattr(response, "duration", None),
    }


# ── Local Whisper ───────────────────────────────────────────────────────────────

def _transcribe_local(audio_bytes: bytes, settings) -> dict:
    """Run whisper locally. Requires: pip install openai-whisper"""
    try:
        import whisper
    except ImportError:
        raise RuntimeError(
            "openai-whisper is not installed. "
            "Run: pip install openai-whisper  OR switch ASR_PROVIDER=openai"
        )

    # Write bytes to a temp file because whisper needs a file path
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    logger.debug("Loading local Whisper model=%s", settings.LOCAL_WHISPER_MODEL)
    model = whisper.load_model(settings.LOCAL_WHISPER_MODEL)
    result = model.transcribe(tmp_path)
    Path(tmp_path).unlink(missing_ok=True)

    return {
        "text": result.get("text", ""),
        "language": result.get("language"),
        "duration_seconds": None,
    }
