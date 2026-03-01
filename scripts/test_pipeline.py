"""
scripts/test_pipeline.py
========================
Quick smoke-test that exercises each system component end-to-end.
Run BEFORE the demo to verify everything is wired correctly.

Usage:
    python scripts/test_pipeline.py
"""

import sys
import asyncio
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s | %(message)s")
logger = logging.getLogger(__name__)

PASS = "✅ PASS"
FAIL = "❌ FAIL"


def check(label: str, ok: bool, detail: str = "") -> None:
    status = PASS if ok else FAIL
    msg = f"{status}  {label}"
    if detail:
        msg += f"  →  {detail}"
    logger.info(msg)


# ── Tests ────────────────────────────────────────────────────────────────────────

def test_config() -> bool:
    try:
        s = get_settings()
        ok = bool(s.OPENAI_API_KEY)
        check("Config loaded + OPENAI_API_KEY present", ok,
              detail="" if ok else "Set OPENAI_API_KEY in .env")
        return ok
    except Exception as exc:
        check("Config", False, str(exc))
        return False


async def test_llm() -> bool:
    try:
        from backend.core.llm_client import chat_completion
        answer, tokens = await chat_completion(
            user_message="قل 'مرحباً' باختصار.",
            context="",
            history=[],
        )
        ok = len(answer) > 0
        check("LLM chat_completion", ok, f"tokens={tokens}, response_len={len(answer)}")
        return ok
    except Exception as exc:
        check("LLM chat_completion", False, str(exc))
        return False


def test_rag_ingest_and_retrieve() -> bool:
    try:
        import tempfile
        from backend.core.rag_engine import ingest_file, retrieve

        # Create a tiny temp text file for testing
        sample_text = (
            "نظام العمل السعودي – المادة الأولى\n"
            "يُطبَّق هذا النظام على كافة العمال والأصحاب العمل في المملكة العربية السعودية.\n"
        )
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", encoding="utf-8", delete=False) as f:
            f.write(sample_text)
            tmp_path = Path(f.name)

        chunks = ingest_file(tmp_path)
        tmp_path.unlink(missing_ok=True)
        check("RAG ingest", chunks > 0, f"chunks={chunks}")

        results = retrieve("نظام العمل")
        check("RAG retrieve", len(results) > 0, f"results={len(results)}")
        return chunks > 0 and len(results) > 0
    except Exception as exc:
        check("RAG", False, str(exc))
        return False


async def test_tts() -> bool:
    try:
        from backend.core.tts_engine import synthesize_speech
        audio_bytes = await synthesize_speech("مرحباً، هذا اختبار.")
        ok = len(audio_bytes) > 0
        check("TTS synthesize_speech", ok, f"bytes={len(audio_bytes)}")
        return ok
    except Exception as exc:
        check("TTS synthesize_speech", False, str(exc))
        return False


async def main() -> None:
    logger.info("=" * 55)
    logger.info("  Legal AI Demo – Pipeline Smoke Test")
    logger.info("=" * 55)

    results = []
    results.append(test_config())
    results.append(await test_llm())
    results.append(test_rag_ingest_and_retrieve())
    results.append(await test_tts())

    passed = sum(results)
    total = len(results)
    logger.info("=" * 55)
    logger.info("Result: %d/%d tests passed.", passed, total)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    asyncio.run(main())
