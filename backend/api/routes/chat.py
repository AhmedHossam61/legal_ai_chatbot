"""
Chat route – /api/chat

POST /api/chat
  Body : ChatRequest
  Returns: ChatResponse  (answer + source chunks)
"""

import logging
from fastapi import APIRouter, HTTPException

from backend.models.schemas import ChatRequest, ChatResponse
from backend.services.chat_service import handle_chat

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a legal question and receive an AI-generated answer.

    - **message**: The user's question (Arabic or English).
    - **history**: Previous conversation turns for context.
    - **use_rag**: Set to false to skip document retrieval and query the LLM directly.
    """
    try:
        return await handle_chat(request)
    except Exception as exc:
        logger.exception("Chat error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
