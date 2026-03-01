"""Sidebar – settings & quick controls."""

import streamlit as st


def render_sidebar() -> None:
    with st.sidebar:
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Saudi_Arabia_coa.svg/140px-Saudi_Arabia_coa.svg.png",
            width=80,
        )
        st.title("⚖️ المساعد القانوني")
        st.caption("نسخة تجريبية – Demo v0.1")
        st.divider()

        # ── Chat Settings ───────────────────────────────────────────────────
        st.subheader("إعدادات المحادثة")
        st.session_state["use_rag"] = st.toggle(
            "تفعيل البحث في المستندات (RAG)",
            value=st.session_state.get("use_rag", True),
            help="عند التفعيل، يبحث النظام في المستندات المرفوعة قبل الإجابة.",
        )

        st.session_state["show_sources"] = st.toggle(
            "إظهار المصادر",
            value=st.session_state.get("show_sources", True),
            help="عرض مقاطع المستندات التي استند إليها النظام في الإجابة.",
        )

        st.divider()

        # ── Clear history ───────────────────────────────────────────────────
        if st.button("🗑️ مسح المحادثة", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()

        st.divider()
        st.caption("مهندس / أحمد حسام عبدالرحمن")
        st.caption("جميع الحقوق محفوظة © 2026")
