"""
Voice route – /api/voice

POST /api/voice/transcribe  – audio → text  (ASR)
POST /api/voice/synthesize  – text  → audio (TTS)
"""

import logging

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response

from backend.models.schemas import TranscriptionResponse, TTSRequest
from backend.core.asr_engine import transcribe_audio
from backend.core.tts_engine import synthesize_speech

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/voice", tags=["Voice"])


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(audio: UploadFile = File(...)) -> TranscriptionResponse:
    """
    Convert an uploaded audio file (WAV, MP3, WebM, M4A, …) to text.
    Supports Arabic and English via OpenAI Whisper.
    """
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file.")

    try:
        result = await transcribe_audio(
            audio_bytes=audio_bytes,
            filename=audio.filename or "audio.webm",
        )
        return TranscriptionResponse(**result)
    except Exception as exc:
        logger.exception("ASR transcription failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/synthesize")
async def synthesize(request: TTSRequest) -> Response:
    """
    Convert text to speech and return an MP3 audio file.
    Supports Arabic text with the configured voice.
    """
    try:
        audio_bytes = await synthesize_speech(
            text=request.text,
            voice=request.voice,
        )
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": 'attachment; filename="response.mp3"'},
        )
    except Exception as exc:
        logger.exception("TTS synthesis failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
