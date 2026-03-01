"""
LLM Client – wraps OpenAI ChatCompletion calls.
Swap the underlying model by changing LLM_MODEL in .env.
"""

import logging
from openai import AsyncOpenAI
from backend.core.config import get_settings
from backend.models.schemas import ChatMessage

logger = logging.getLogger(__name__)


def _build_client() -> AsyncOpenAI:
    settings = get_settings()
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


# Module-level client instance (re-used across requests)
_client: AsyncOpenAI | None = None


def get_llm_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = _build_client()
    return _client


async def chat_completion(
    user_message: str,
    context: str = "",
    history: list[ChatMessage] | None = None,
) -> tuple[str, int]:
    """
    Call the LLM and return (answer_text, tokens_used).

    Parameters
    ----------
    user_message : str  – The current user query.
    context      : str  – RAG-retrieved context to inject.
    history      : list – Previous chat turns (role/content pairs).
    """
    settings = get_settings()
    client = get_llm_client()

    # ── Build message list ──────────────────────────────────────────────────
    messages: list[dict] = [{"role": "system", "content": settings.SYSTEM_PROMPT}]

    if history:
        for msg in history[-6:]:          # keep last 6 turns to limit tokens
            messages.append({"role": msg.role, "content": msg.content})

    # Inject RAG context before the user message if available
    if context:
        messages.append({
            "role": "system",
            "content": f"السياق القانوني المسترجع:\n\n{context}\n\nاستخدم هذا السياق للإجابة.",
        })

    messages.append({"role": "user", "content": user_message})

    # ── API call ────────────────────────────────────────────────────────────
    logger.debug("Calling LLM model=%s", settings.LLM_MODEL)
    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=messages,
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
    )

    answer = response.choices[0].message.content or ""
    tokens = response.usage.total_tokens if response.usage else 0
    return answer, tokens
