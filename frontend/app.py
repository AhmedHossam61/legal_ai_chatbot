"""
Legal AI Demo – Streamlit Frontend
===================================
Run with:
    streamlit run frontend/app.py

Tabs:
  • 💬 المحادثة           – Chat with the AI lawyer
  • 📄 رفع المستندات      – Upload & manage legal documents
  • 🎙️ التفاعل الصوتي     – Record speech → get audio reply
  • ℹ️  حول النظام        – System info / health
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ──────────────────────────────────
st.set_page_config(
    page_title="المساعد القانوني الذكي",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from frontend.components.sidebar import render_sidebar
from frontend.components.chat_tab import render_chat_tab
from frontend.components.documents_tab import render_documents_tab
from frontend.components.voice_tab import render_voice_tab
from frontend.components.about_tab import render_about_tab

# ── Sidebar ─────────────────────────────────────────────────────────────────────
render_sidebar()

# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style='text-align:center; padding: 1rem 0'>
        <h1 style='font-size:2.2rem'>⚖️ المساعد القانوني الذكي</h1>
        <p style='color:#888'>نظام قانوني ذكي مدعوم بالذكاء الاصطناعي – نسخة تجريبية</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Tabs ─────────────────────────────────────────────────────────────────────────
tabs = st.tabs(["💬 المحادثة", "📄 رفع المستندات", "🎙️ التفاعل الصوتي", "ℹ️ حول النظام"])

with tabs[0]:
    render_chat_tab()

with tabs[1]:
    render_documents_tab()

with tabs[2]:
    render_voice_tab()

with tabs[3]:
    render_about_tab()
