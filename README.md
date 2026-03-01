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

```bash
pip install -r requirements.txt
```

Key packages installed:

| Package | Purpose |
|---------|---------|
| `google-genai` | Gemini TTS + ASR (inline audio) |
| `langchain-google-genai` | Gemini LLM + Embeddings via LangChain |
| `langchain-chroma` | Vector store integration |
| `fastapi` + `uvicorn` | REST API backend |
| `streamlit` | Web frontend |
| `pymupdf` + `docx2txt` | PDF / DOCX document parsing |

---

### Step 4 â€“ Configure environment variables

Copy the example file and open it in any text editor:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` and set your Gemini API key:

```env
GEMINI_API_KEY=AIza...your-key-here...
```

All other values have sensible defaults and do **not** need to be changed for the demo.

<details>
<summary>Full .env reference</summary>

```env
GEMINI_API_KEY=AIza...           # Required â€“ get free at aistudio.google.com/apikey

LLM_MODEL=gemini-2.0-flash       # Chat model (free tier)
LLM_TEMPERATURE=0.2
LLM_MAX_TOKENS=2048

EMBED_MODEL=models/text-embedding-004  # Embedding model (free tier)
RAG_TOP_K=4
CHUNK_SIZE=800
CHUNK_OVERLAP=100

ASR_PROVIDER=gemini              # gemini (free) | local_whisper (offline)
ASR_MODEL=gemini-2.0-flash

TTS_PROVIDER=gemini              # gemini (free) | gtts (lighter)
TTS_MODEL=gemini-2.5-flash-preview-tts
TTS_VOICE=Aoede                  # Aoede | Kore | Puck | Fenrir | Charon | â€¦

DEBUG=true
```

</details>

---

### Step 5 â€“ (Optional) Ingest Saudi legal documents

Drop any PDF, DOCX, or TXT legal files into `backend/data/saudi_legal_samples/`, then run:

```bash
python scripts/ingest_legal_docs.py
```

This embeds the documents into ChromaDB so the AI can answer questions based on them.  
You can skip this step and still use the chat â€“ the AI will answer from its base knowledge.

---

### Step 6 â€“ Run the smoke test

Verify that all components work before the demo:

```bash
python scripts/test_pipeline.py
```

Expected output:
```
INFO     âœ… PASS  Config loaded + GEMINI_API_KEY present
INFO     âœ… PASS  Gemini LLM chat_completion  â†’  tokens=â€¦
INFO     âœ… PASS  RAG ingest  â†’  chunks=2
INFO     âœ… PASS  RAG retrieve  â†’  results=1
INFO     âœ… PASS  Gemini TTS synthesize_speech (WAV)  â†’  bytes=â€¦
INFO     Result: 4/4 tests passed.
```

---

### Step 7 â€“ Start the backend

Open a terminal and run:

```bash
uvicorn backend.main:app --reload --port 8000
```

- `--reload` watches for code changes (great for development)
- The API is now live at **http://localhost:8000**
- Interactive API docs (Swagger UI): **http://localhost:8000/docs**

---

### Step 8 â€“ Start the frontend

Open a **second terminal** (with the virtual environment activated), then run:

```bash
streamlit run frontend/app.py
```

The browser will open automatically at **http://localhost:8501**.  
If it doesn't, open it manually.

---

### Step 9 â€“ Use the app

| Tab | What to do |
|-----|-----------|
| **ðŸ’¬ Ø§Ù„Ù…Ø­Ø§Ø¯Ø«Ø©** | Type a legal question in Arabic or English and press Enter |
| **ðŸ“„ Ø±ÙØ¹ Ø§Ù„Ù…Ø³ØªÙ†Ø¯Ø§Øª** | Upload a PDF/DOCX/TXT contract or regulation |
| **ðŸŽ™ï¸ Ø§Ù„ØªÙØ§Ø¹Ù„ Ø§Ù„ØµÙˆØªÙŠ** | Record or upload audio â†’ get a spoken AI answer |
| **â„¹ï¸ Ø­ÙˆÙ„ Ø§Ù„Ù†Ø¸Ø§Ù…** | Click "ØªØ­Ø¯ÙŠØ« Ø§Ù„Ø­Ø§Ù„Ø©" to confirm all components are green |

---

### Running the tests

```bash
pytest tests/ -v
```

---

## ðŸ”§ Configuration Reference

All settings live in [backend/core/config.py](backend/core/config.py) and are loaded from `.env`.

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | â€“ | **Required** â€“ free at aistudio.google.com |
| `LLM_MODEL` | `gemini-2.0-flash` | Chat LLM (free tier) |
| `EMBED_MODEL` | `models/text-embedding-004` | Embedding model (free tier) |
| `ASR_PROVIDER` | `gemini` | `gemini` or `local_whisper` |
| `TTS_PROVIDER` | `gemini` | `gemini` or `gtts` |
| `TTS_MODEL` | `gemini-2.5-flash-preview-tts` | Gemini TTS model |
| `TTS_VOICE` | `Aoede` | One of 30 available voices |
| `RAG_TOP_K` | `4` | Chunks retrieved per query |

**Available TTS voices:** Aoede, Kore, Puck, Fenrir, Charon, Leda, Orus, Zephyr, Autonoe, Sulafat, and 20 more. See the [Gemini TTS docs](https://ai.google.dev/gemini-api/docs/speech-generation#voice-options).

---

## ðŸ—ï¸ Architecture

```
User (Browser)
    â”‚
    â–¼
Streamlit Frontend (port 8501)
    â”‚  httpx calls
    â–¼
FastAPI Backend (port 8000)
    â”œâ”€â”€ /api/chat        â†’ chat_service â†’ Gemini LLM + ChromaDB RAG
    â”œâ”€â”€ /api/documents   â†’ document_service â†’ ChromaDB
    â””â”€â”€ /api/voice       â†’ asr_engine (Gemini) + tts_engine (Gemini TTS)
```

---

## ðŸ“‹ Demo Scope (as per proposal)

- [x] Web application with professional UI
- [x] LLM integration for legal text analysis (Gemini 2.0 Flash)
- [x] Document upload + analysis (PDF, DOCX, TXT) via RAG
- [x] ASR â€“ voice to text (Gemini multimodal)
- [x] TTS â€“ text to audio (Gemini 2.5 Flash Preview TTS)
- [x] RAG over a sample of Saudi legal regulations (ChromaDB)

---

## ðŸ› ï¸ Troubleshooting

| Problem | Solution |
|---------|---------|
| `GEMINI_API_KEY not set` | Make sure `.env` exists and contains your key |
| Backend not reachable on port 8000 | Check that `uvicorn` is running in the first terminal |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside the active `.venv` |
| Empty transcription from voice tab | Ensure audio is loud/clear; try uploading a WAV file instead |
| ChromaDB version error | Run `pip install --upgrade chromadb langchain-chroma` |

---

*مهندس / أحمد حسام عبدالرحمن – فبراير 2026*
