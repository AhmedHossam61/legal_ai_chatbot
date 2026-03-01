# Legal AI Demo – Arabic Legal Assistant

Proof-of-concept legal assistant focused on Saudi legal content.
It combines a FastAPI backend, Streamlit frontend, Gemini-powered chat/voice, and ChromaDB retrieval.

---

## Highlights

- Arabic/English legal chat via Gemini
- RAG over uploaded PDF/DOCX/TXT documents
- Voice workflow: record/upload audio → transcribe → answer → synthesize speech
- Upload pipeline hardened with clearer error reporting
- Embedding pipeline includes resilient fallbacks when Gemini embedding endpoints are unavailable

---

## Project Structure

```text
legal_ai_chatbot/
├── backend/
│   ├── api/routes/                 # chat, documents, voice APIs
│   ├── core/                       # config, llm/rag/asr/tts, embeddings wrapper
│   ├── models/                     # pydantic schemas
│   ├── services/                   # chat + document orchestration
│   ├── uploads/                    # uploaded files + registry
│   └── vector_store/               # ChromaDB persistence
├── frontend/
│   ├── app.py
│   └── components/                 # tabs + API client
├── scripts/                        # ingest + smoke test
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

---

## Prerequisites

| Dependency | Version | Check |
|---|---:|---|
| Python | 3.11+ | `python --version` |
| pip | 23+ | `pip --version` |
| Git | any | `git --version` |

Get a Gemini API key from: <https://aistudio.google.com/apikey>

---

## Quick Start

1. Clone and enter the repo:
   ```bash
   git clone https://github.com/AhmedHossam61/legal_ai_chatbot.git
   cd legal_ai_chatbot
   ```

2. Create and activate virtual environment:
   - Windows PowerShell:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - macOS/Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```bash
   copy .env.example .env   # Windows
   # cp .env.example .env   # macOS/Linux
   ```
   Set at least:
   ```env
   GEMINI_API_KEY=AIza...your-key...
   ```

5. Start backend:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
   - API: <http://localhost:8000>
   - Docs: <http://localhost:8000/docs>

6. Start frontend (new terminal):
   ```bash
   streamlit run frontend/app.py
   ```
   UI: <http://localhost:8501>

---

## Recent Fixes (March 2026)

### 1) Frontend import path error fixed

If you run with `streamlit run frontend/app.py`, component imports now use `from components...`.
This resolves `ModuleNotFoundError: No module named 'frontend'`.

### 2) Upload errors are now clearer

- Uploaded filenames are sanitized before saving.
- Document processing/parsing failures return HTTP `422` with readable details.
- Frontend now shows backend `detail` text in error messages.

So instead of a generic `500 Internal Server Error`, you now get a specific cause.

### 3) Embedding resiliency for RAG

RAG embeddings now follow this fallback chain:

1. Try configured `EMBED_MODEL`
2. Retry with `models/embedding-001`
3. Fallback to local deterministic embedding

This keeps ingestion/retrieval working even when Gemini embedding endpoints return 404 for your key/region/API route.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | required | Gemini API key |
| `LLM_MODEL` | `gemini-2.0-flash` | Chat model |
| `EMBED_MODEL` | `models/embedding-001` | Preferred embedding model |
| `ASR_PROVIDER` | `gemini` | `gemini` or `local_whisper` |
| `TTS_PROVIDER` | `gemini` | `gemini` or `gtts` |
| `TTS_MODEL` | `gemini-2.5-flash-preview-tts` | TTS model |
| `TTS_VOICE` | `Aoede` | TTS voice |
| `RAG_TOP_K` | `4` | Number of retrieved chunks |
| `CHUNK_SIZE` | `800` | Chunk size |
| `CHUNK_OVERLAP` | `100` | Chunk overlap |

---

## Validation Commands

- Run smoke test:
  ```bash
  python scripts/test_pipeline.py
  ```
- Run tests:
  ```bash
  pytest tests/ -v
  ```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: frontend` in Streamlit | Run `streamlit run frontend/app.py` and keep component imports as `from components...` |
| Upload fails with parser-related message | Re-upload file; error now includes exact backend `detail` |
| RAG embedding 404 on Gemini models | Expected in some setups; fallback path keeps RAG functional |
| TTS returns `429 RESOURCE_EXHAUSTED` | Free-tier quota reached; retry later or change plan/model |
| Backend unreachable | Ensure `uvicorn` is running on port `8000` |

---

Maintainer: Eng. Ahmed Hossam Abdelrahman
