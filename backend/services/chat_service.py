"""
Chat Service – orchestrates RAG retrieval + LLM completion.

Separating this from the route keeps the API layer thin and
makes unit-testing the business logic straightforward.
"""

import logging
from backend.models.schemas import ChatRequest, ChatResponse
from backend.core.rag_engine import retrieve, build_context_string
from backend.core.llm_client import chat_completion

logger = logging.getLogger(__name__)


async def handle_chat(request: ChatRequest) -> ChatResponse:
    """
    Full pipeline for a single chat turn:
      1. (Optional) Retrieve relevant document chunks via RAG.
      2. Build a structured context string.
      3. Call the LLM with the context + user question.
      4. Return the answer and source references.
    """
    sources = []
    context = ""

    if request.use_rag:
        logger.debug("RAG retrieval for query: %.80s", request.message)
        sources = retrieve(request.message)
        if sources:
            context = build_context_string(sources)
            logger.debug("Retrieved %d chunks", len(sources))
        else:
            logger.debug("No relevant chunks found – answering from base knowledge")

    answer, tokens = await chat_completion(
        user_message=request.message,
        context=context,
        history=request.history,
    )

    return ChatResponse(
        answer=answer,
        sources=sources,
        tokens_used=tokens,
    )
