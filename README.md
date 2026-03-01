# âš–ï¸ Legal AI Demo â€“ Ù†Ø¸Ø§Ù… Ù‚Ø§Ù†ÙˆÙ†ÙŠ Ø°ÙƒÙŠ

Ù†Ù…ÙˆØ°Ø¬ Ø£ÙˆÙ„ÙŠ Ù„Ù†Ø¸Ø§Ù… Ø°ÙƒØ§Ø¡ Ø§ØµØ·Ù†Ø§Ø¹ÙŠ Ù…ØªØ®ØµØµ ÙÙŠ Ø§Ù„Ø£Ù†Ø¸Ù…Ø© ÙˆØ§Ù„ØªØ´Ø±ÙŠØ¹Ø§Øª Ø§Ù„Ø³Ø¹ÙˆØ¯ÙŠØ©.  
**Ø§Ù„Ù…Ø¯Ø©:** Ø£Ø³Ø¨ÙˆØ¹ ÙˆØ§Ø­Ø¯ Ù„Ù„Ø¨Ù†Ø§Ø¡ØŒ Ø´Ù‡Ø± ÙƒØ§Ù…Ù„ Ù„Ù„Ø¯Ø¹Ù… Ø§Ù„Ù…Ø¬Ø§Ù†ÙŠ.

---

## ðŸ—‚ï¸ Ù‡ÙŠÙƒÙ„ Ø§Ù„Ù…Ø´Ø±ÙˆØ¹

```
legal_ai_chatbot/
â”‚
â”œâ”€â”€ backend/                    â† FastAPI Backend
â”‚   â”œâ”€â”€ api/routes/
â”‚   â”‚   â”œâ”€â”€ chat.py             â† POST /api/chat
â”‚   â”‚   â”œâ”€â”€ documents.py        â† POST /api/documents/upload  |  GET/DELETE
â”‚   â”‚   â””â”€â”€ voice.py            â† POST /api/voice/transcribe  |  /synthesize
â”‚   â”‚
â”‚   â”œâ”€â”€ core/
â”‚   â”‚   â”œâ”€â”€ config.py           â† All settings (loaded from .env)
â”‚   â”‚   â”œâ”€â”€ llm_client.py       â† Gemini LLM chat
â”‚   â”‚   â”œâ”€â”€ rag_engine.py       â† ChromaDB ingest + retrieval
â”‚   â”‚   â”œâ”€â”€ asr_engine.py       â† Gemini multimodal speech-to-text
â”‚   â”‚   â””â”€â”€ tts_engine.py       â† Gemini TTS / gTTS text-to-speech
â”‚   â”‚
â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â””â”€â”€ schemas.py          â† Pydantic request/response models
â”‚   â”‚
â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â”œâ”€â”€ chat_service.py     â† RAG + LLM orchestration
â”‚   â”‚   â””â”€â”€ document_service.py â† File saving, registry, vector deletion
â”‚   â”‚
â”‚   â”œâ”€â”€ data/saudi_legal_samples/   â† Drop Saudi law PDFs here
â”‚   â”œâ”€â”€ uploads/                â† User-uploaded documents (auto-created)
â”‚   â”œâ”€â”€ vector_store/           â† ChromaDB persistence (auto-created)
â”‚   â””â”€â”€ main.py                 â† FastAPI app + CORS + health check
â”‚
â”œâ”€â”€ frontend/                   â† Streamlit Frontend
â”‚   â”œâ”€â”€ app.py                  â† Entry point (4 tabs)
â”‚   â””â”€â”€ components/
â”‚       â”œâ”€â”€ api_client.py       â† All HTTP calls to the backend
â”‚       â”œâ”€â”€ sidebar.py          â† Settings sidebar
â”‚       â”œâ”€â”€ chat_tab.py         â† Conversational UI
â”‚       â”œâ”€â”€ documents_tab.py    â† Upload + manage documents
â”‚       â”œâ”€â”€ voice_tab.py        â† Record â†’ transcribe â†’ answer â†’ speak
â”‚       â””â”€â”€ about_tab.py        â† Health check + system info
â”‚
â”œâ”€â”€ scripts/
â”‚   â”œâ”€â”€ ingest_legal_docs.py    â† Bulk-ingest documents into ChromaDB
â”‚   â””â”€â”€ test_pipeline.py        â† Smoke test (run before demo)
â”‚
â”œâ”€â”€ tests/
â”‚   â”œâ”€â”€ test_chat.py
â”‚   â””â”€â”€ test_documents.py
â”‚
â”œâ”€â”€ .env.example                â† Copy to .env and fill in your key
â”œâ”€â”€ requirements.txt
â””â”€â”€ README.md
```

---

## ðŸš€ How to Run the Project

### Prerequisites

| Tool | Minimum Version | Check |
|------|----------------|-------|
| Python | 3.11+ | `python --version` |
| pip | 23+ | `pip --version` |
| Git | any | `git --version` |

You also need a **free Gemini API key** â€“ get one at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

---

### Step 1 â€“ Clone the repository

```bash
git clone https://github.com/AhmedHossam61/legal_ai_chatbot.git
cd legal_ai_chatbot
```

---

### Step 2 â€“ Create and activate a virtual environment

**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD)**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` at the start of your prompt after activation.

---

### Step 3 â€“ Install dependencies
## Legal AI Demo – Arabic Legal Assistant

This repository hosts a proof-of-concept legal assistant focused on Saudi laws. It combines a FastAPI backend, a Streamlit frontend, and Google Gemini models for chat, retrieval-augmented generation (RAG), speech-to-text, and text-to-speech.

---

## Highlights

- Chat experience in Arabic or English powered by Gemini 2.0 Flash
- Upload Saudi regulations or contracts (PDF/DOCX/TXT) and query them via RAG
- Voice mode: record audio, transcribe it, and listen to the AI’s spoken reply
- Complete end-to-end pipeline (ingestion script, smoke tests, automated health panel)

---

## Project Structure

```
legal_ai_chatbot/
├── backend/                FastAPI code (API routes, services, core modules)
├── frontend/               Streamlit UI (chat, documents, voice, about tabs)
├── scripts/                Utility scripts (ingest + smoke test)
├── tests/                  Pytest-based unit tests
├── requirements.txt        Python dependencies
├── .env.example            Sample environment variables
└── README.md
```

---

## Prerequisites

| Dependency | Minimum Version | Command to verify |
|------------|-----------------|-------------------|
| Python     | 3.11            | `python --version` |
| pip        | 23              | `pip --version`    |
| Git        | any             | `git --version`    |

You also need a free **Gemini API key** from <https://aistudio.google.com/apikey>.

---

## Quick Start

1. **Clone the repo**
    ```bash
    git clone https://github.com/AhmedHossam61/legal_ai_chatbot.git
    cd legal_ai_chatbot
    ```

2. **Create & activate a virtual environment**
    - PowerShell: `python -m venv .venv && .\.venv\Scripts\Activate.ps1`
    - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables**
    ```bash
    copy .env.example .env        # or: cp .env.example .env
    ```
    Edit `.env` and set:
    ```env
    GEMINI_API_KEY=AIza...your-key...
    ```
    Optional overrides (defaults shown):
    ```env
    LLM_MODEL=gemini-2.0-flash
    EMBED_MODEL=models/text-embedding-004
    ASR_PROVIDER=gemini         # or local_whisper
    TTS_PROVIDER=gemini         # or gtts
    TTS_MODEL=gemini-2.5-flash-preview-tts
    TTS_VOICE=Aoede             # see docs for the full voice list
    ```

5. **(Optional) Ingest sample regulations**
    Place documents in `backend/data/saudi_legal_samples/` and run:
    ```bash
    python scripts/ingest_legal_docs.py
    ```

6. **Run the smoke test**
    ```bash
    python scripts/test_pipeline.py
    ```
    This checks config, LLM, RAG, and TTS before the demo.

7. **Start the backend (terminal #1)**
    ```bash
    uvicorn backend.main:app --reload --port 8000
    ```
    - API base URL: <http://localhost:8000>
    - Swagger docs: <http://localhost:8000/docs>

8. **Start the frontend (terminal #2)**
    ```bash
    streamlit run frontend/app.py
    ```
    Visit <http://localhost:8501> in your browser.

9. **Interact with the demo**
    | Tab | Purpose |
    |-----|---------|
    | Chat | Ask legal questions, view cited RAG snippets |
    | Documents | Upload/manage PDFs, DOCX, TXT files |
    | Voice | Record/upload audio → transcribe → answer → speak |
    | About | Health status (Gemini key, vector store, etc.) |

10. **Run the automated tests**
     ```bash
     pytest tests/ -v
     ```

---

## Key Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `GEMINI_API_KEY` | (required) | Free key from Google AI Studio |
| `LLM_MODEL` | `gemini-2.0-flash` | Chat model used by the assistant |
| `EMBED_MODEL` | `models/text-embedding-004` | Embeddings for ChromaDB |
| `ASR_PROVIDER` | `gemini` | `gemini` or `local_whisper` |
| `TTS_PROVIDER` | `gemini` | `gemini` or `gtts` |
| `TTS_MODEL` | `gemini-2.5-flash-preview-tts` | Text-to-speech model |
| `TTS_VOICE` | `Aoede` | Any Gemini TTS voice (Kore, Puck, Fenrir, etc.) |
| `RAG_TOP_K` | `4` | Number of chunks returned per query |

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Backend | FastAPI, Uvicorn, Pydantic |
| Frontend | Streamlit + httpx |
| LLM / Embeddings | Gemini (via `langchain-google-genai`) |
| Vector Store | ChromaDB |
| Speech | Gemini ASR + Gemini TTS (fallback to gTTS/local Whisper) |
| Testing | Pytest, pytest-asyncio |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `GEMINI_API_KEY not set` | Ensure `.env` exists and contains the key |
| `ModuleNotFoundError` | Activate `.venv` and reinstall requirements |
| Backend unavailable on port 8000 | Confirm `uvicorn` is running and not blocked |
| Voice tab returns empty text | Record a louder clip or upload WAV/MP3 directly |
| ChromaDB schema errors | Re-run `pip install -r requirements.txt` to sync versions |

---

Maintainer: Eng. Ahmed Hossam Abdelrahman (Feb 2026)
| `TTS_VOICE` | `Aoede` | One of 30 available voices |
