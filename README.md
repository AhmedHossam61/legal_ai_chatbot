# ⚖️ Legal AI Demo – نظام قانوني ذكي

نموذج أولي لنظام ذكاء اصطناعي متخصص في الأنظمة والتشريعات السعودية.  
**المدة:** أسبوع واحد للبناء، شهر كامل للدعم المجاني.

---

## 🗂️ هيكل المشروع

```
legal_ai_chatbot/
│
├── backend/                    ← FastAPI Backend
│   ├── api/routes/
│   │   ├── chat.py             ← POST /api/chat
│   │   ├── documents.py        ← POST /api/documents/upload  |  GET/DELETE
│   │   └── voice.py            ← POST /api/voice/transcribe  |  /synthesize
│   │
│   ├── core/
│   │   ├── config.py           ← All settings (loaded from .env)
│   │   ├── llm_client.py       ← OpenAI chat + streaming
│   │   ├── rag_engine.py       ← ChromaDB ingest + retrieval
│   │   ├── asr_engine.py       ← Whisper speech-to-text
│   │   └── tts_engine.py       ← OpenAI / gTTS text-to-speech
│   │
│   ├── models/
│   │   └── schemas.py          ← Pydantic request/response models
│   │
│   ├── services/
│   │   ├── chat_service.py     ← RAG + LLM orchestration
│   │   └── document_service.py ← File saving, registry, vector deletion
│   │
│   ├── data/saudi_legal_samples/   ← Drop Saudi law PDFs here
│   ├── uploads/                ← User-uploaded documents (auto-created)
│   ├── vector_store/           ← ChromaDB persistence (auto-created)
│   └── main.py                 ← FastAPI app + CORS + health check
│
├── frontend/                   ← Streamlit Frontend
│   ├── app.py                  ← Entry point (4 tabs)
│   └── components/
│       ├── api_client.py       ← All HTTP calls to the backend
│       ├── sidebar.py          ← Settings sidebar
│       ├── chat_tab.py         ← Conversational UI
│       ├── documents_tab.py    ← Upload + manage documents
│       ├── voice_tab.py        ← Record → transcribe → answer → speak
│       └── about_tab.py        ← Health check + system info
│
├── scripts/
│   ├── ingest_legal_docs.py    ← Bulk-ingest documents into ChromaDB
│   └── test_pipeline.py        ← Smoke test (run before demo)
│
├── tests/
│   ├── test_chat.py
│   └── test_documents.py
│
├── .env.example                ← Copy to .env and fill in your keys
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
copy .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. (Optional) Ingest Saudi legal documents
Drop PDF/DOCX/TXT files into `backend/data/saudi_legal_samples/`, then:
```bash
python scripts/ingest_legal_docs.py
```

### 4. Run the smoke test
```bash
python scripts/test_pipeline.py
```

### 5. Start the backend
```bash
uvicorn backend.main:app --reload --port 8000
```

### 6. Start the frontend (new terminal)
```bash
streamlit run frontend/app.py
```

Open **http://localhost:8501** in your browser.  
API docs: **http://localhost:8000/docs**

---

## 🔧 Configuration

All settings live in `backend/core/config.py` and are loaded from `.env`.

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | – | Required |
| `LLM_MODEL` | `gpt-4o-mini` | LLM model name |
| `ASR_PROVIDER` | `openai` | `openai` or `local_whisper` |
| `TTS_PROVIDER` | `openai` | `openai` or `gtts` |
| `RAG_TOP_K` | `4` | Number of chunks retrieved per query |

---

## 🏗️ Architecture

```
User (Browser)
    │
    ▼
Streamlit Frontend (port 8501)
    │  httpx calls
    ▼
FastAPI Backend (port 8000)
    ├── /api/chat        → chat_service → LLM + RAG
    ├── /api/documents   → document_service → ChromaDB
    └── /api/voice       → asr_engine + tts_engine → OpenAI
```

---

## 📋 Demo Scope (as per proposal)

- [x] Web application with professional UI
- [x] LLM integration for legal text analysis
- [x] Document upload + analysis (PDF, DOCX, TXT)
- [x] ASR – voice to text (Whisper)
- [x] TTS – text to audio (OpenAI TTS)
- [x] RAG over a sample of Saudi legal regulations

---

*مهندس / أحمد حسام عبدالرحمن – فبراير 2026*
