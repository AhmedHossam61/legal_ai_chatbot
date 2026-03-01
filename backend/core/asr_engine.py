"""
ASR Engine – Speech-to-Text.

Supports two providers (set ASR_PROVIDER in .env):
  • "gemini"         – Gemini multimodal model for transcription (free tier)
  • "local_whisper"  – openai-whisper library running locally (offline, slower)
"""

import logging
import tempfile
from pathlib import Path

from backend.core.config import get_settings

logger = logging.getLogger(__name__)

# Map common file extensions to valid MIME types for the Gemini API
_MIME_MAP = {
    ".wav":  "audio/wav",
    ".mp3":  "audio/mp3",
    ".m4a":  "audio/aac",
    ".aac":  "audio/aac",
    ".ogg":  "audio/ogg",
    ".flac": "audio/flac",
    ".webm": "audio/webm",
    ".aiff": "audio/aiff",
}


async def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> dict:
    """
    Transcribe audio bytes and return:
      {"text": str, "language": str | None, "duration_seconds": float | None}

    Parameters
    ----------
    audio_bytes : bytes  – Raw audio data (wav, mp3, m4a, ogg, flac, webm…)
    filename    : str    – Original filename (used to infer MIME type)
    """
    settings = get_settings()
    provider = settings.ASR_PROVIDER.lower()

    if provider == "gemini":
        return await _transcribe_gemini(audio_bytes, filename, settings)
    elif provider == "local_whisper":
        return _transcribe_local(audio_bytes, settings)
    else:
        raise ValueError(f"Unknown ASR_PROVIDER: {provider!r}. Use 'gemini' or 'local_whisper'.")


# ── Gemini ASR (multimodal transcription) ───────────────────────────────────────

async def _transcribe_gemini(audio_bytes: bytes, filename: str, settings) -> dict:
    """
    Use a Gemini multimodal model to transcribe audio.
    Audio is passed inline (max 20 MB) which avoids the Files API for demo-sized clips.
    """
    import asyncio
    from google import genai
    from google.genai import types

    suffix = Path(filename).suffix.lower()
    mime_type = _MIME_MAP.get(suffix, "audio/wav")

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = (
        "Please transcribe this audio verbatim. "
        "If the speech is in Arabic, transcribe in Arabic. "
        "Return ONLY the transcription text, nothing else."
    )

    logger.debug("Calling Gemini ASR, model=%s, mime=%s, size=%d bytes",
                 settings.ASR_MODEL, mime_type, len(audio_bytes))

    # Run the synchronous Gemini SDK call in a thread executor
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.models.generate_content(
            model=settings.ASR_MODEL,
            contents=[
                prompt,
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
            ],
        )
    )

    text = response.text.strip() if response.text else ""
    return {"text": text, "language": None, "duration_seconds": None}


# ── Local Whisper ───────────────────────────────────────────────────────────────

def _transcribe_local(audio_bytes: bytes, settings) -> dict:
    """Run Whisper locally. Requires: pip install openai-whisper"""
    try:
        import whisper
    except ImportError:
        raise RuntimeError(
            "openai-whisper is not installed. "
            "Run: pip install openai-whisper  OR switch ASR_PROVIDER=gemini"
        )

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
