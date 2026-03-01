"""
tests/test_chat.py
Unit tests for the chat service and LLM client.
Run with: pytest tests/
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.models.schemas import ChatRequest, ChatResponse, ChatMessage


# ── Helpers ─────────────────────────────────────────────────────────────────────

def make_chat_request(message: str = "ما هي حقوق العامل؟", use_rag: bool = False) -> ChatRequest:
    return ChatRequest(message=message, history=[], use_rag=use_rag)


# ── Tests ────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_chat_service_no_rag():
    """Chat service should return a ChatResponse even with RAG disabled."""
    from backend.services.chat_service import handle_chat

    mock_answer = "العامل له حق في راتبه وإجازاته السنوية."
    mock_tokens = 45

    with patch("backend.services.chat_service.chat_completion", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = (mock_answer, mock_tokens)

        result = await handle_chat(make_chat_request(use_rag=False))

    assert isinstance(result, ChatResponse)
    assert result.answer == mock_answer
    assert result.tokens_used == mock_tokens
    assert result.sources == []


@pytest.mark.asyncio
async def test_chat_service_with_rag():
    """Chat service should retrieve chunks and pass context to the LLM."""
    from backend.services.chat_service import handle_chat
    from backend.models.schemas import SourceChunk

    fake_chunks = [
        SourceChunk(content="نص قانوني تجريبي", source="نظام_العمل.pdf", page=1)
    ]
    mock_answer = "استناداً إلى نظام العمل، للعامل عدة حقوق."
    mock_tokens = 80

    with (
        patch("backend.services.chat_service.retrieve", return_value=fake_chunks),
        patch("backend.services.chat_service.build_context_string", return_value="نص قانوني تجريبي"),
        patch("backend.services.chat_service.chat_completion", new_callable=AsyncMock) as mock_llm,
    ):
        mock_llm.return_value = (mock_answer, mock_tokens)
        result = await handle_chat(make_chat_request(use_rag=True))

    assert result.answer == mock_answer
    assert len(result.sources) == 1
    assert result.sources[0].source == "نظام_العمل.pdf"


def test_chat_message_role_validation():
    """ChatMessage should reject invalid roles."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ChatMessage(role="unknown_role", content="test")


def test_chat_request_empty_message():
    """ChatRequest should reject empty messages."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ChatRequest(message="", history=[], use_rag=True)
