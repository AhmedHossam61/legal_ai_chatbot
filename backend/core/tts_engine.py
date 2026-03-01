"""
TTS Engine – Text-to-Speech.

Supports two providers (set TTS_PROVIDER in .env):
  • "openai"  – OpenAI TTS API    (high quality, requires API key)
  • "gtts"    – Google TTS        (free, lighter, requires internet)
"""

import logging
import io

from backend.core.config import get_settings

logger = logging.getLogger(__name__)


async def synthesize_speech(text: str, voice: str | None = None) -> bytes:
    """
    Convert *text* to audio and return MP3 bytes.

    Parameters
    ----------
    text  : str        – Text to synthesize (Arabic or English).
    voice : str | None – Override the default TTS_VOICE from .env.
    """
    settings = get_settings()
    provider = settings.TTS_PROVIDER.lower()

    if provider == "openai":
        return await _tts_openai(text, voice or settings.TTS_VOICE, settings)
    elif provider == "gtts":
        return _tts_gtts(text)
    else:
        raise ValueError(f"Unknown TTS_PROVIDER: {provider!r}. Use 'openai' or 'gtts'.")


# ── OpenAI TTS ──────────────────────────────────────────────────────────────────

async def _tts_openai(text: str, voice: str, settings) -> bytes:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    logger.debug("Calling OpenAI TTS, model=%s voice=%s", settings.TTS_MODEL, voice)
    response = await client.audio.speech.create(
        model=settings.TTS_MODEL,
        voice=voice,
        input=text,
        response_format="mp3",
    )
    # response.content is the raw bytes
    return response.content


# ── gTTS (Google TTS – free fallback) ──────────────────────────────────────────

def _tts_gtts(text: str) -> bytes:
    """Generate speech using gTTS. Requires: pip install gTTS"""
    try:
        from gtts import gTTS
    except ImportError:
        raise RuntimeError(
            "gTTS is not installed. Run: pip install gTTS  OR switch TTS_PROVIDER=openai"
        )

    # Detect language (basic heuristic – if Arabic chars present, use 'ar')
    lang = "ar" if any("\u0600" <= c <= "\u06ff" for c in text) else "en"
    logger.debug("Generating gTTS audio, lang=%s", lang)

    tts = gTTS(text=text, lang=lang, slow=False)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return buffer.read()
