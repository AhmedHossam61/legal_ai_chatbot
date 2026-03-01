"""
LLM Client – wraps Google Gemini chat calls via langchain-google-genai.
Swap the model by changing LLM_MODEL in .env (e.g., gemini-2.0-flash, gemini-1.5-pro).
"""

import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from backend.core.config import get_settings
from backend.models.schemas import ChatMessage

logger = logging.getLogger(__name__)

# Module-level LLM instance (re-used across requests)
_llm: ChatGoogleGenerativeAI | None = None


def get_llm() -> ChatGoogleGenerativeAI:
    global _llm
    if _llm is None:
        settings = get_settings()
        _llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=settings.LLM_TEMPERATURE,
            max_output_tokens=settings.LLM_MAX_TOKENS,
        )
    return _llm


async def chat_completion(
    user_message: str,
    context: str = "",
    history: list[ChatMessage] | None = None,
) -> tuple[str, int]:
    """
    Call Gemini and return (answer_text, tokens_used).

    Parameters
    ----------
    user_message : str  – The current user query.
    context      : str  – RAG-retrieved context to inject.
    history      : list – Previous chat turns (role/content pairs).
    """
    settings = get_settings()
    llm = get_llm()

    # ── Build message list ──────────────────────────────────────────────────
    messages = [SystemMessage(content=settings.SYSTEM_PROMPT)]

    if history:
        for msg in history[-6:]:          # keep last 6 turns to limit tokens
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))

    # Inject RAG context before the user message if available
    if context:
        messages.append(SystemMessage(
            content=f"السياق القانوني المسترجع:\n\n{context}\n\nاستخدم هذا السياق للإجابة."
        ))

    messages.append(HumanMessage(content=user_message))

    # ── API call ────────────────────────────────────────────────────────────
    logger.debug("Calling Gemini model=%s", settings.LLM_MODEL)
    response = await llm.ainvoke(messages)

    answer = response.content if isinstance(response.content, str) else str(response.content)

    # Extract token usage if available
    tokens = 0
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        tokens = getattr(response.usage_metadata, "total_tokens", 0) or 0

    return answer, tokens
