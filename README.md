# Legal AI Chatbot - Arabic Legal Assistant

A production-ready AI-powered legal assistant designed primarily for Arabic legal content.
It enables lawyers, researchers, and legal professionals to query uploaded legal documents through natural language conversation, hear spoken answers, and manage their document library - all in one web interface.

---

## What Does This Project Do?

1. **Answers legal questions in Arabic and English** - You upload your legal documents (court rulings, laws, contracts, case files), ask questions in plain language, and get precise answers sourced directly from those documents.

2. **Retrieves relevant passages from your documents** - Before answering, the system finds the most relevant sections of your uploaded documents and feeds them to the AI. This means you get grounded, document-sourced answers rather than generic AI guesses.

3. **Speaks answers aloud and understands spoken questions** - The voice tab lets you record or upload audio, transcribes it using Gemini's speech recognition, generates a document-grounded answer, then synthesizes that answer back into audio you can play or download.

4. **Manages your document library** - Upload PDF, DOCX, and TXT files through the browser. The system parses, chunks, embeds, and indexes them automatically. You can list all indexed documents and delete any you no longer need.

---

## Features

### 1. Multi-Turn Legal Chat

- Powered by **Gemini** (`gemini-2.0-flash` by default)
- Maintains full conversation history across turns so you can ask follow-up questions
- System prompt enforces a strict legal assistant persona - concise, sourced, professional
- Arabic and English input/output both supported
- Chat history downloadable as JSON from the sidebar

### 2. Retrieval-Augmented Generation (RAG)

- Every chat question is first embedded and matched against your indexed documents
- Top-K most relevant text chunks (default: 4) are injected into the prompt as context
- **ChromaDB** stores all vector embeddings persistently on disk
- Documents are split into overlapping chunks (default: 800 tokens / 100 overlap) to preserve context across page boundaries
- Full ingestion pipeline: file save -> text extraction -> chunking -> embedding -> vector store upsert

### 3. Voice Interaction

| Step | Technology | Detail |
|---|---|---|
| Audio input | Browser mic or file upload | WAV, MP3, OGG, WEBM accepted |
| Transcription (ASR) | Gemini multimodal (`gemini-2.0-flash`) | Audio bytes sent directly to Gemini with a transcription prompt |
| Answer generation | Gemini + RAG | Same pipeline as chat tab |
| Speech synthesis (TTS) | Gemini TTS (`gemini-2.5-flash-preview-tts`) | PCM audio wrapped into WAV and returned to browser |
| TTS fallback | gTTS (Google Text-to-Speech) | Used automatically when Gemini TTS quota is exceeded |

Voice answers are playable inline and downloadable as `.wav` files.

### 4. Resilient Embedding Pipeline

The embedding pipeline never blocks ingestion. It tries three levels before failing:

1. **Primary** - Configured `EMBED_MODEL` (default `models/embedding-001`) via Gemini API
2. **Secondary fallback** - Hard-coded `models/embedding-001` retry (catches 404 on preview models)
3. **Local fallback** - Deterministic 256-dimensional hashing embedding computed entirely offline

This means the system continues to work even when Gemini embedding endpoints return 404 for your API key, region, or model tier.

### 5. Document Management

- Upload via drag-and-drop or file picker in the browser
- Filenames are automatically sanitized (removes unsafe characters including Arabic Unicode that some OS file systems reject)
- Processing errors return HTTP 422 with a readable message (not a generic 500)
- Indexed document list shows filename and chunk count
- One-click delete removes both the file and its vector store entries

### 6. Health Dashboard

- `/health` endpoint reports:
  - API status
  - Embedding model name in use
  - LLM model name
  - Indexed document count
  - Vector store status
- Visible in the "About" tab of the UI

---

## Architecture

```
Browser (Streamlit UI)
    |
    |  HTTP REST
    v
FastAPI Backend  (localhost:8000)
    |
    +---> Chat Service
    |         |---> RAG Engine ---> ChromaDB (vector_store/)
    |         |         |---> GeminiEmbeddings (3-level fallback)
    |         |---> LLM Engine ---> Gemini (gemini-2.0-flash)
    |
    +---> Document Service
    |         |---> PyMuPDF (PDF)
    |         |---> Docx2txt (DOCX)
    |         |---> UTF-8 reader (TXT)
    |         |---> RAG Engine (ingest)
    |
    +---> Voice Service
              |---> ASR Engine ---> Gemini multimodal
              |---> Chat Service (answer)
              |---> TTS Engine ---> Gemini TTS / gTTS fallback
```

---

## Project Structure

```
legal_ai_chatbot/
+-- backend/
|   +-- api/
|   |   +-- routes/
|   |       +-- chat.py          # POST /api/chat
|   |       +-- documents.py     # POST/GET/DELETE /api/documents
|   |       +-- voice.py         # POST /api/voice/transcribe, /synthesize
|   +-- core/
|   |   +-- config.py            # All settings via pydantic-settings + .env
|   |   +-- embeddings.py        # Custom GeminiEmbeddings with 3-level fallback
|   |   +-- rag_engine.py        # ChromaDB + LangChain retriever
|   |   +-- llm_engine.py        # Gemini LLM wrapper
|   |   +-- asr_engine.py        # Gemini multimodal ASR
|   |   +-- tts_engine.py        # Gemini TTS / gTTS fallback
|   +-- models/
|   |   +-- schemas.py           # Pydantic request/response models
|   +-- services/
|   |   +-- chat_service.py      # RAG + LLM orchestration
|   |   +-- document_service.py  # File save, parse, ingest, registry
|   +-- uploads/                 # Saved uploaded files + registry.json
|   +-- vector_store/            # ChromaDB persistent storage
|   +-- main.py                  # FastAPI app, CORS, lifespan, /health
+-- frontend/
|   +-- app.py                   # Streamlit entrypoint, tab layout, sidebar
|   +-- components/
|       +-- api_client.py        # All HTTP calls to backend
|       +-- chat_tab.py          # Chat UI with history
|       +-- documents_tab.py     # Upload / list / delete UI
|       +-- voice_tab.py         # Record / transcribe / speak UI
|       +-- about_tab.py         # System info and health check
+-- scripts/
|   +-- ingest_docs.py           # Bulk ingest documents from a folder
|   +-- test_pipeline.py         # Smoke test: config / LLM / RAG / TTS
+-- tests/                       # pytest test suite
+-- .env.example                 # Template for environment variables
+-- requirements.txt
+-- README.md
```

---

## Prerequisites

| Requirement | Version | How to Check |
|---|---|---|
| Python | 3.11+ | `python --version` |
| pip | 23+ | `pip --version` |
| Git | any | `git --version` |
| Gemini API Key | - | [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey) |

A Gemini API key is the only external account required. The free tier works for development and testing.

---

## Setup and Run

**Step 1 - Clone the repository**

```bash
git clone https://github.com/AhmedHossam61/legal_ai_chatbot.git
cd legal_ai_chatbot
```

**Step 2 - Create a virtual environment**

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Step 3 - Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 4 - Create your environment file**

```bash
copy .env.example .env    # Windows
cp .env.example .env      # macOS/Linux
```

Open `.env` and set your Gemini API key:

```env
GEMINI_API_KEY=AIza...your-key-here...
```

All other values have working defaults and can be left as-is to start.

**Step 5 - (Optional) Pre-ingest a folder of documents**

```bash
python scripts/ingest_docs.py --folder path/to/your/documents
```

You can also upload documents through the UI after the app starts.

**Step 6 - Start the backend**

```bash
uvicorn backend.main:app --reload --port 8000
```

- REST API: [http://localhost:8000](http://localhost:8000)
- Interactive API docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

**Step 7 - Start the frontend (new terminal, venv activated)**

```bash
streamlit run frontend/app.py
```

- Web UI: [http://localhost:8501](http://localhost:8501)

**Step 8 - Validate everything is working**

```bash
python scripts/test_pipeline.py
```

Expected output: 4/4 checks pass (Config, LLM, RAG, TTS).

---

## Using the Application

### Chat Tab

1. Type your legal question in Arabic or English in the message box at the bottom
2. Press Enter or click Send
3. The assistant retrieves relevant passages from your indexed documents, then generates an answer
4. Continue the conversation - it remembers previous messages
5. Use the sidebar to clear history or download the conversation as JSON

### Documents Tab

1. Click Browse or drag a file into the upload area
2. Supported formats: PDF, DOCX, TXT
3. Click Upload - the file is parsed, chunked, embedded, and indexed automatically
4. The document list below shows all currently indexed files with their chunk counts
5. Click Delete next to any document to remove it from the index

### Voice Tab

1. Click Record to capture audio from your microphone, or upload an audio file
2. Click Transcribe - your speech is converted to text using Gemini
3. The transcribed text is shown and automatically sent as a chat question
4. The answer appears as text and is synthesized into speech
5. Use the audio player to listen to the answer, or click Download to save the WAV file

### About Tab

- Shows the current system health status
- Displays which models are loaded (LLM, embedding, TTS)
- Shows the number of documents indexed
- Useful for verifying your configuration is active

---

## Configuration Reference

All settings live in `.env`. The full list with defaults:

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | **required** | Your Google Gemini API key |
| `LLM_MODEL` | `gemini-2.0-flash` | Gemini model for chat and voice answers |
| `EMBED_MODEL` | `models/embedding-001` | Preferred Gemini embedding model |
| `ASR_PROVIDER` | `gemini` | Speech-to-text provider: `gemini` or `local_whisper` |
| `ASR_MODEL` | `gemini-2.0-flash` | Model used for transcription (Gemini provider) |
| `TTS_PROVIDER` | `gemini` | Text-to-speech provider: `gemini` or `gtts` |
| `TTS_MODEL` | `gemini-2.5-flash-preview-tts` | Gemini TTS model |
| `TTS_VOICE` | `Aoede` | Gemini TTS voice name |
| `RAG_TOP_K` | `4` | Number of document chunks retrieved per question |
| `CHUNK_SIZE` | `800` | Characters per document chunk |
| `CHUNK_OVERLAP` | `100` | Overlapping characters between consecutive chunks |
| `UPLOAD_DIR` | `backend/uploads` | Directory where uploaded files are saved |
| `VECTOR_STORE_DIR` | `backend/vector_store` | ChromaDB persistence directory |
| `DEBUG` | `false` | Enables verbose logging when set to `true` |

---

## API Reference

All endpoints are available under `http://localhost:8000`. Interactive docs at `/docs`.

| Method | Endpoint | Request Body | Response | Description |
|---|---|---|---|---|
| GET | `/health` | - | `{status, llm_model, embed_model, docs_indexed, vector_store_status}` | System health check |
| POST | `/api/chat` | `{message, history[]}` | `{answer, sources[]}` | Send a chat message, get grounded answer |
| POST | `/api/documents/upload` | multipart file | `{filename, chunks_indexed}` | Upload and index a document |
| GET | `/api/documents` | - | `[{filename, chunk_count}]` | List all indexed documents |
| DELETE | `/api/documents/{filename}` | - | `{deleted}` | Remove a document from the index |
| POST | `/api/voice/transcribe` | multipart audio file | `{transcript}` | Transcribe audio to text |
| POST | `/api/voice/synthesize` | `{text}` | WAV audio bytes | Synthesize text to speech |

---

## Tech Stack

| Layer | Technology | Role |
|---|---|---|
| Backend framework | FastAPI | REST API, request validation, async support |
| Frontend | Streamlit | Web UI, tabs, audio recording |
| LLM | Google Gemini (`gemini-2.0-flash`) | Legal Q&A, conversation |
| TTS | Gemini TTS / gTTS | Speech synthesis |
| ASR | Gemini multimodal | Speech-to-text |
| Embeddings | Custom GeminiEmbeddings (LangChain) | Vector representation of text chunks |
| Vector store | ChromaDB | Persistent similarity search |
| LLM framework | LangChain | RAG chain, text splitter, retriever |
| PDF parsing | PyMuPDF | Extract text from PDF files |
| DOCX parsing | Docx2txt | Extract text from Word documents |
| Config | pydantic-settings | Type-safe settings from `.env` |
| Testing | pytest | Unit and integration tests |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'frontend'` | Streamlit resolves imports from the `frontend/` directory | Always start with `streamlit run frontend/app.py` from the project root |
| Upload returns 500 on Arabic-named file | Unsafe characters in filename | Fixed: filenames are sanitized automatically since March 2026 |
| Upload returns 422 with a parsing message | File is corrupt, password-protected, or unsupported format | Try a different file; the error message will indicate the exact cause |
| RAG embedding 404 from Gemini | Model not available on your key tier or region | Fixed: 3-level fallback keeps RAG working; no action needed |
| TTS returns `429 RESOURCE_EXHAUSTED` | Gemini TTS free-tier quota exceeded | Wait for quota reset, or set `TTS_PROVIDER=gtts` in `.env` |
| Backend unreachable from frontend | `uvicorn` not running or wrong port | Make sure `uvicorn backend.main:app --port 8000` is running |
| `No documents indexed` warning in chat | No files uploaded yet | Upload at least one document from the Documents tab |
| Streamlit shows blank page | Frontend started before backend was ready | Refresh the browser; backend must be running first |

---

## Changelog

### March 2026

- **Fixed** `ModuleNotFoundError: No module named 'frontend'` in all four Streamlit component files
- **Fixed** Arabic/Unicode filename crash on document upload with `_safe_filename()` sanitizer
- **Improved** Upload error reporting: processing failures now return HTTP 422 with descriptive detail instead of generic 500
- **Added** `GeminiEmbeddings` custom LangChain wrapper with 3-level fallback (primary model -> embedding-001 -> local hashing)
- **Changed** Default `EMBED_MODEL` from `text-embedding-004` to `models/embedding-001` for broader API key compatibility
- **Added** `_raise_for_status_with_detail()` in `api_client.py` so frontend displays backend error detail text

---

Maintainer: Eng. Ahmed Hossam Abdelrahman
