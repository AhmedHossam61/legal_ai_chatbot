"""
scripts/ingest_legal_docs.py
============================
Bulk-ingest all documents in backend/data/saudi_legal_samples/ into ChromaDB.

Usage:
    python scripts/ingest_legal_docs.py
    python scripts/ingest_legal_docs.py --dir path/to/custom/docs
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to path so backend imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.config import get_settings
from backend.core.rag_engine import ingest_file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger(__name__)


def ingest_directory(directory: Path) -> None:
    settings = get_settings()
    supported = set(settings.ALLOWED_EXTENSIONS)
    files = [f for f in directory.rglob("*") if f.suffix.lower() in supported]

    if not files:
        logger.warning("No supported files found in %s", directory)
        return

    logger.info("Found %d file(s) to ingest.", len(files))
    total_chunks = 0

    for file_path in files:
        try:
            chunks = ingest_file(file_path)
            total_chunks += chunks
            logger.info("✅ %-40s → %d chunks", file_path.name, chunks)
        except Exception as exc:
            logger.error("❌ Failed to ingest %s: %s", file_path.name, exc)

    logger.info("=" * 60)
    logger.info("Done. Total chunks created: %d", total_chunks)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest legal documents into ChromaDB.")
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path(get_settings().LEGAL_DOCS_DIR),
        help="Directory containing legal documents to ingest.",
    )
    args = parser.parse_args()

    if not args.dir.is_dir():
        logger.error("Directory not found: %s", args.dir)
        sys.exit(1)

    logger.info("Ingesting documents from: %s", args.dir)
    ingest_directory(args.dir)


if __name__ == "__main__":
    main()
