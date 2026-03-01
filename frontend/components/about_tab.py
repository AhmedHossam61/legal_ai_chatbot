"""About Tab – system health and technical overview."""

import streamlit as st
from frontend.components.api_client import health_check


def render_about_tab() -> None:
    st.subheader("ℹ️ حول النظام")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### المساعد القانوني الذكي – نسخة تجريبية

        **الوصف:**  
        نظام ذكاء اصطناعي متخصص في الأنظمة والتشريعات السعودية،
        يجمع بين قدرات اللغة الطبيعية والبحث الدلالي في الوثائق القانونية.

        **المميزات:**
        - 💬 دردشة ذكية باللغة العربية مع نموذج GPT
        - 📄 رفع وتحليل العقود والوثائق القانونية (RAG)
        - 🎙️ تحويل الصوت إلى نص (Whisper)
        - 🔊 تحويل الإجابات إلى صوت (OpenAI TTS)
        - 🔍 بحث دلالي في قاعدة المعارف القانونية

        **التقنيات المستخدمة:**
        | المكوّن | التقنية |
        |---------|---------|
        | LLM | OpenAI GPT-4o-mini |
        | Embeddings | text-embedding-3-small |
        | Vector DB | ChromaDB |
        | RAG Framework | LangChain |
        | ASR | OpenAI Whisper |
        | TTS | OpenAI TTS |
        | Backend | FastAPI |
        | Frontend | Streamlit |
        """)

    with col2:
        st.markdown("### حالة النظام")
        if st.button("🔄 تحديث الحالة", use_container_width=True):
            st.rerun()

        try:
            health = health_check()
            st.success(f"✅ الخادم يعمل – إصدار {health.get('version', '?')}")

            components = health.get("components", {})
            for key, value in components.items():
                icon = "✅" if value not in ("MISSING", "not_found") else "❌"
                label = {
                    "openai_key": "مفتاح OpenAI",
                    "vector_store": "قاعدة المتجهات",
                    "uploads_dir": "مجلد الرفع",
                    "llm_model": "نموذج اللغة",
                    "asr_provider": "مزود ASR",
                    "tts_provider": "مزود TTS",
                }.get(key, key)
                st.markdown(f"{icon} **{label}:** `{value}`")

        except Exception as exc:
            st.error(f"❌ الخادم غير متاح: {exc}")
            st.info("تأكد من تشغيل الخادم:\n```\nuvicorn backend.main:app --reload\n```")

    st.divider()
    st.markdown("""
    **مقدم المشروع:** مهندس / أحمد حسام عبدالرحمن  
    **التاريخ:** فبراير 2026  
    *هذه نسخة تجريبية لأغراض التقييم والعرض فقط.*
    """)
