"""
TTS Engine – Text-to-Speech.

Supports two providers (set TTS_PROVIDER in .env):
  • "gemini"  – Gemini 2.5 Flash TTS (free tier, high quality, Arabic-capable)
  • "gtts"    – Google TTS           (free, lighter, requires internet)

Gemini TTS returns raw PCM (LINEAR16, 24 kHz, mono).
This module wraps it in a WAV container so browsers and st.audio() can play it.
"""

import io
import wave
import logging
import asyncio

from backend.core.config import get_settings

logger = logging.getLogger(__name__)


# ── WAV helper ──────────────────────────────────────────────────────────────────

def _pcm_to_wav(pcm_data: bytes, sample_rate: int = 24000,
               channels: int = 1, sample_width: int = 2) -> bytes:
    """Wrap raw PCM bytes in a WAV container and return the result as bytes."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)   # 2 bytes = 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)
    buffer.seek(0)
    return buffer.read()


# ── Public API ──────────────────────────────────────────────────────────────────

async def synthesize_speech(text: str, voice: str | None = None) -> bytes:
    """
    Convert *text* to audio and return WAV bytes.

    Parameters
    ----------
    text  : str        – Text to synthesize (Arabic or English).
    voice : str | None – Override the default TTS_VOICE from .env.
                         Gemini voices: Aoede, Kore, Puck, Fenrir, Charon, …
    """
    settings = get_settings()
    provider = settings.TTS_PROVIDER.lower()

    if provider == "gemini":
        return await _tts_gemini(text, voice or settings.TTS_VOICE, settings)
    elif provider == "gtts":
        return _tts_gtts(text)
    else:
        raise ValueError(f"Unknown TTS_PROVIDER: {provider!r}. Use 'gemini' or 'gtts'.")


# ── Gemini TTS ──────────────────────────────────────────────────────────────────

async def _tts_gemini(text: str, voice: str, settings) -> bytes:
    """
    Call gemini-2.5-flash-preview-tts and return WAV bytes.
    The model outputs raw PCM (LINEAR16, 24 kHz, mono) which we wrap in WAV.
    """
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    logger.debug("Calling Gemini TTS, model=%s voice=%s", settings.TTS_MODEL, voice)

    # Run the synchronous SDK call in a thread executor so we don't block the event loop
    response = await asyncio.get_running_loop().run_in_executor(
        None,
        lambda: client.models.generate_content(
            model=settings.TTS_MODEL,          # gemini-2.5-flash-preview-tts
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice,  # e.g. "Aoede"
                        )
                    )
                ),
            ),
        )
    )

    # Extract raw PCM bytes from the response
    pcm_data: bytes = response.candidates[0].content.parts[0].inline_data.data
    return _pcm_to_wav(pcm_data)


# ── gTTS (free fallback) ────────────────────────────────────────────────────────

def _tts_gtts(text: str) -> bytes:
    """Generate speech using gTTS. Requires: pip install gTTS"""
    try:
        from gtts import gTTS
    except ImportError:
        raise RuntimeError(
            "gTTS is not installed. Run: pip install gTTS  OR switch TTS_PROVIDER=gemini"
        )

    lang = "ar" if any("\u0600" <= c <= "\u06ff" for c in text) else "en"
    logger.debug("Generating gTTS audio, lang=%s", lang)

    tts = gTTS(text=text, lang=lang, slow=False)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return buffer.read()
