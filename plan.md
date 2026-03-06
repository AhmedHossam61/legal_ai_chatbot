# RAG System Enhancement Plan – Migrate to Qdrant (Docker)

## Overview

The current RAG system uses **ChromaDB** as its local vector store, which stores embeddings on disk in the `backend/vector_store/` directory. While functional for development, ChromaDB has key limitations at scale:

- No true client-server architecture (file-locked, single-process)
- No web UI for inspecting/debugging vector collections
- No native support for payload filtering, advanced HNSW tuning, or multi-tenancy
- Poor horizontal scalability

**Goal**: Replace ChromaDB with **Qdrant** running in a Docker container. Alongside the database migration, we will introduce several RAG quality improvements: improved text splitting for Arabic documents, similarity score threshold filtering, document-level metadata filtering, hybrid search (dense + sparse BM25), and a streaming LLM response endpoint.

---

## Architecture After Migration

```
┌──────────────────────────────────────────────┐
│              FastAPI Backend                 │
│                                              │
│  ┌──────────────┐     ┌──────────────────┐   │
│  │  chat_service│────▶│   rag_engine.py  │   │
│  └──────────────┘     │  (Qdrant client) │   │
│                       └────────┬─────────┘   │
│  ┌──────────────────┐          │              │
│  │ document_service │──────────┘              │
│  └──────────────────┘                        │
└──────────────┬───────────────────────────────┘
               │  HTTP / gRPC
               ▼
   ┌───────────────────────┐
   │  Qdrant  (Docker)     │
   │  Port 6333 (REST)     │
   │  Port 6334 (gRPC)     │
   │  Collection: legal_docs│
   └───────────────────────┘
```

---

## Phase 1 – Infrastructure: Qdrant via Docker

### 1.1 `docker-compose.yml` [NEW]

Create `docker-compose.yml` at the project root to run Qdrant as a service.

```yaml
version: "3.9"
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: legal_ai_qdrant
    ports:
      - "6333:6333"   # REST API + Web UI
      - "6334:6334"   # gRPC
    volumes:
      - qdrant_storage:/qdrant/storage
    restart: unless-stopped

volumes:
  qdrant_storage:
```

**Start Qdrant:**
```bash
docker compose up -d qdrant
```

**Verify:** open `http://localhost:6333/dashboard` in a browser — the Qdrant Web UI should be visible.

---

## Phase 2 – Configuration Updates

### 2.1 [MODIFY] `backend/core/config.py`

Add Qdrant connection settings and remove the `VECTOR_STORE_DIR` dependency.

**Changes:**
- Remove: `VECTOR_STORE_DIR`
- Add:
  ```python
  QDRANT_HOST: str = "localhost"
  QDRANT_PORT: int = 6333
  QDRANT_COLLECTION: str = "legal_docs"
  QDRANT_VECTOR_SIZE: int = 768     # matches text-embedding-004 output dim
  QDRANT_PREFER_GRPC: bool = False  # set True for higher throughput
  SIMILARITY_SCORE_THRESHOLD: float = 0.45  # filter out low-relevance chunks
  ```

### 2.2 [MODIFY] `.env.example`

Add the new Qdrant variables:
```ini
# ── Qdrant Vector DB ────────────────────────────────────────────────────────────
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=legal_docs
QDRANT_VECTOR_SIZE=768
QDRANT_PREFER_GRPC=false
SIMILARITY_SCORE_THRESHOLD=0.45
```

---

## Phase 3 – RAG Engine Rewrite

### 3.1 [MODIFY] `backend/core/rag_engine.py`

This is the core change. Replace all ChromaDB logic with Qdrant.

**Key changes:**

#### a) Qdrant client initialization (singleton)
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

_qdrant_client: QdrantClient | None = None

def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        settings = get_settings()
        _qdrant_client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            prefer_grpc=settings.QDRANT_PREFER_GRPC,
        )
        # Ensure collection exists
        collections = [c.name for c in _qdrant_client.get_collections().collections]
        if settings.QDRANT_COLLECTION not in collections:
            _qdrant_client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=VectorParams(
                    size=settings.QDRANT_VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )
    return _qdrant_client
```

#### b) `ingest_file()` — upsert points into Qdrant
```python
from qdrant_client.models import PointStruct
import uuid

def ingest_file(file_path: Path) -> int:
    settings = get_settings()
    raw_docs = _load_document(file_path)
    chunks = _split_documents(raw_docs, settings)   # improved splitter (see §3.2)
    embeddings = GeminiEmbeddings(model=settings.EMBED_MODEL, api_key=settings.GEMINI_API_KEY)
    doc_id = _doc_id(file_path)
    client = get_qdrant_client()

    points = []
    for i, chunk in enumerate(chunks):
        vector = embeddings.embed_documents([chunk.page_content])[0]
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}_{i}"))
        points.append(PointStruct(
            id=point_id,
            vector=vector,
            payload={
                "content": chunk.page_content,
                "source": file_path.name,
                "doc_id": doc_id,
                "page": chunk.metadata.get("page"),
                "chunk_index": i,
            },
        ))

    # Upsert in batches of 64
    for batch_start in range(0, len(points), 64):
        client.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=points[batch_start:batch_start + 64],
        )
    return len(points)
```

#### c) `retrieve()` — similarity search with score threshold
```python
def retrieve(query: str, doc_id_filter: str | None = None) -> list[SourceChunk]:
    settings = get_settings()
    client = get_qdrant_client()
    embeddings = GeminiEmbeddings(model=settings.EMBED_MODEL, api_key=settings.GEMINI_API_KEY)
    query_vector = embeddings.embed_query(query)

    query_filter = None
    if doc_id_filter:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        query_filter = Filter(
            must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id_filter))]
        )

    results = client.search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=settings.RAG_TOP_K,
        query_filter=query_filter,
        with_payload=True,
        score_threshold=settings.SIMILARITY_SCORE_THRESHOLD,
    )

    return [
        SourceChunk(
            content=hit.payload["content"],
            source=hit.payload.get("source", "unknown"),
            page=hit.payload.get("page"),
        )
        for hit in results
    ]
```

#### d) Delete by `doc_id` (for `delete_document`)
```python
def delete_document_vectors(doc_id: str) -> None:
    settings = get_settings()
    client = get_qdrant_client()
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    client.delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=Filter(
            must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
        ),
    )
```

### 3.2 Improved Arabic / Legal Text Splitter

The current splitter uses basic separators. We will add Arabic-aware separators:

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
    separators=["\n\n", "\n", ".", "،", "؛", ":", " ", ""],
)
```

---

## Phase 4 – Document Service Update

### 4.1 [MODIFY] `backend/services/document_service.py`

- Replace inline ChromaDB deletion code in `delete_document()` with a call to the new `delete_document_vectors(doc_id)` from `rag_engine.py`.
- Remove `langchain_chroma` and `langchain_google_genai` imports from this file (they only existed for the deletion workaround).

---

## Phase 5 – API Enhancements

### 5.1 [MODIFY] `backend/models/schemas.py`

Add optional `doc_id` filter to `ChatRequest`:
```python
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list)
    use_rag: bool = True
    doc_id_filter: Optional[str] = None  # NEW: scope RAG to a single document
```

Add `score` field to `SourceChunk`:
```python
class SourceChunk(BaseModel):
    content: str
    source: str
    page: Optional[int] = None
    score: Optional[float] = None   # NEW: relevance score from Qdrant
```

### 5.2 [MODIFY] `backend/services/chat_service.py`

Pass `request.doc_id_filter` through to `retrieve()`:
```python
sources = retrieve(request.message, doc_id_filter=request.doc_id_filter)
```

### 5.3 [MODIFY] `backend/main.py` – Health Check

Update the health check to ping Qdrant instead of checking `VECTOR_STORE_DIR`:
```python
try:
    client = get_qdrant_client()
    info = client.get_collection(settings.QDRANT_COLLECTION)
    components["qdrant"] = f"ok ({info.points_count} vectors)"
except Exception as exc:
    components["qdrant"] = f"ERROR: {exc}"
```

---

## Phase 6 – Dependency Updates

### 6.1 [MODIFY] `requirements.txt`

**Add:**
```
qdrant-client>=1.9.0
```

**Remove (or keep as optional):**
```
langchain-chroma
chromadb
```

> **Note:** Only remove ChromaDB after migration is fully verified. Keep it in a `[optional]` section first.

---

## Phase 7 – Migration Script

### 7.1 [NEW] `scripts/migrate_to_qdrant.py`

A one-shot script that:
1. Reads all documents from the existing JSON registry (`uploads/registry.json`).
2. Re-ingests each file through the new `ingest_file()` function (which now writes to Qdrant).
3. Prints a summary report.

```bash
python scripts/migrate_to_qdrant.py
```

---

## Phase 8 – Testing Updates

### 8.1 [MODIFY] `tests/test_documents.py` and `tests/test_chat.py`

Update all mocks that previously patched `langchain_chroma.Chroma` to patch the new Qdrant `get_qdrant_client()` function and `qdrant_client.QdrantClient`.

### 8.2 [NEW] `tests/test_rag_engine.py`

New unit test file covering:
- `ingest_file()` – mock Qdrant client and assert `upsert` is called with correct point structure.
- `retrieve()` – mock `client.search` and assert `SourceChunk` list is correctly built.
- `delete_document_vectors()` – mock `client.delete` and assert filter payload is correct.
- Score threshold filtering – assert that results below the threshold score are excluded.

Run tests with:
```bash
pytest tests/ -v
```

---

## Verification Plan

### Automated Tests

```bash
# Run the full test suite
pytest tests/ -v

# Run only the new RAG engine tests
pytest tests/test_rag_engine.py -v
```

### Manual Verification

1. **Start Qdrant:**
   ```bash
   docker compose up -d qdrant
   ```

2. **Start the backend:**
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

3. **Health check – confirm Qdrant appears as `ok`:**
   ```bash
   curl http://localhost:8000/health
   ```
   Expected: `"qdrant": "ok (0 vectors)"` (before ingestion).

4. **Upload a test document:**
   Use the Streamlit frontend (`streamlit run frontend/app.py`) or:
   ```bash
   curl -F "file=@Palestine-Penal-Code-Gaza-Egyptian-1939-Arabic.pdf" http://localhost:8000/documents/upload
   ```

5. **Verify vectors in Qdrant Dashboard:**
   Open `http://localhost:6333/dashboard` → Collections → `legal_docs` → confirm points were inserted.

6. **Run a chat query with RAG enabled:**
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "ما هي عقوبة السرقة؟", "use_rag": true}'
   ```
   Expected: answer with `sources` list populated and non-empty.

7. **Delete the document and verify vectors are removed:**
   ```bash
   curl -X DELETE http://localhost:8000/documents/{doc_id}
   # Then check Qdrant dashboard – points for that doc_id should be gone
   ```

8. **Test document-scoped RAG** (new `doc_id_filter` field):
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "...", "use_rag": true, "doc_id_filter": "<doc_id>"}'
   ```

---

## Summary of Files Changed

| File | Change |
|---|---|
| `docker-compose.yml` | **NEW** – Qdrant Docker service |
| `backend/core/config.py` | Replace `VECTOR_STORE_DIR` with Qdrant settings |
| `backend/core/rag_engine.py` | **Rewrite** – ChromaDB → Qdrant, score threshold, doc filter |
| `backend/services/document_service.py` | Use new `delete_document_vectors()` helper |
| `backend/services/chat_service.py` | Pass `doc_id_filter` to `retrieve()` |
| `backend/models/schemas.py` | Add `doc_id_filter` to `ChatRequest`, `score` to `SourceChunk` |
| `backend/main.py` | Update health check to ping Qdrant |
| `requirements.txt` | Add `qdrant-client`, phase out `langchain-chroma`/`chromadb` |
| `scripts/migrate_to_qdrant.py` | **NEW** – one-time migration script |
| `tests/test_rag_engine.py` | **NEW** – unit tests for the rewritten engine |
| `tests/test_chat.py` | Update mocks for Qdrant client |
| `tests/test_documents.py` | Update mocks for Qdrant client |
| `.env.example` | Add Qdrant environment variables |

---

## Estimated Effort

| Phase | Effort |
|---|---|
| Phase 1 – Docker setup | 30 min |
| Phase 2 – Config | 15 min |
| Phase 3 – RAG Engine rewrite | 2–3 hours |
| Phase 4 – Document service update | 30 min |
| Phase 5 – API enhancements | 45 min |
| Phase 6 – Dependencies | 15 min |
| Phase 7 – Migration script | 1 hour |
| Phase 8 – Tests | 2 hours |
| **Total** | **~7–8 hours** |
