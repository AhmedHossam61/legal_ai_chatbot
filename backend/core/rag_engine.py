"""
RAG Engine – document ingestion and retrieval using ChromaDB + LangChain.

Two entry-points:
  • ingest_file(path)   – chunk a document and upsert into ChromaDB
  • retrieve(query)     – return top-K relevant chunks for a query
"""

import logging
import hashlib
from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from backend.core.config import get_settings
from backend.models.schemas import SourceChunk

logger = logging.getLogger(__name__)

# ── Helpers ─────────────────────────────────────────────────────────────────────

def _get_vectorstore() -> Chroma:
    settings = get_settings()
    embeddings = OpenAIEmbeddings(
        model=settings.EMBED_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
    )
    return Chroma(
        persist_directory=settings.VECTOR_STORE_DIR,
        embedding_function=embeddings,
        collection_name="legal_docs",
    )


def _load_document(file_path: Path) -> list:
    """Load a document and return LangChain Document objects."""
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        loader = PyMuPDFLoader(str(file_path))
    elif suffix == ".docx":
        loader = Docx2txtLoader(str(file_path))
    elif suffix == ".txt":
        loader = TextLoader(str(file_path), encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
    return loader.load()


def _doc_id(file_path: Path) -> str:
    """Deterministic ID based on file path."""
    return hashlib.md5(str(file_path).encode()).hexdigest()


# ── Public API ──────────────────────────────────────────────────────────────────

def ingest_file(file_path: Path) -> int:
    """
    Chunk the document at *file_path* and store embeddings in ChromaDB.
    Returns the number of chunks created.
    """
    settings = get_settings()
    logger.info("Ingesting file: %s", file_path.name)

    raw_docs = _load_document(file_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", "،", " ", ""],
    )
    chunks = splitter.split_documents(raw_docs)

    # Attach source metadata to each chunk
    doc_id = _doc_id(file_path)
    for chunk in chunks:
        chunk.metadata["source"] = file_path.name
        chunk.metadata["doc_id"] = doc_id

    vs = _get_vectorstore()
    vs.add_documents(chunks)
    logger.info("Created %d chunks for %s", len(chunks), file_path.name)
    return len(chunks)


def retrieve(query: str) -> list[SourceChunk]:
    """
    Retrieve the top-K most relevant chunks for *query*.
    Returns a list of SourceChunk objects ready for the API response.
    """
    settings = get_settings()
    vs = _get_vectorstore()

    results = vs.similarity_search(query, k=settings.RAG_TOP_K)

    return [
        SourceChunk(
            content=doc.page_content,
            source=doc.metadata.get("source", "unknown"),
            page=doc.metadata.get("page"),
        )
        for doc in results
    ]


def build_context_string(chunks: list[SourceChunk]) -> str:
    """Concatenate chunks into a single context block for the LLM prompt."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[{i}] (المصدر: {chunk.source})\n{chunk.content}")
    return "\n\n---\n\n".join(parts)
