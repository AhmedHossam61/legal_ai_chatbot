"""
Documents Tab – upload legal documents and manage the knowledge base.
"""

import streamlit as st
from components.api_client import upload_document, list_documents, delete_document


def render_documents_tab() -> None:
    st.subheader("📄 إدارة المستندات القانونية")
    st.caption("ارفع عقوداً أو أنظمة سعودية أو أي مستند قانوني ليقوم النظام بتحليله والإجابة بناءً عليه.")

    # ── Upload ──────────────────────────────────────────────────────────────
    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "اختر ملفاً",
            type=["pdf", "docx", "txt"],
            help="الحد الأقصى 20 ميغابايت. الأنواع المدعومة: PDF, DOCX, TXT",
        )

    with col2:
        st.write("")
        st.write("")
        if st.button("⬆️ رفع وتحليل", use_container_width=True, type="primary"):
            if uploaded_file is None:
                st.warning("الرجاء اختيار ملف أولاً.")
            else:
                with st.spinner(f"جاري رفع {uploaded_file.name} وإنشاء الفهرس…"):
                    try:
                        result = upload_document(uploaded_file.read(), uploaded_file.name)
                        st.success(
                            f"✅ تم رفع **{result['filename']}** بنجاح! "
                            f"({result.get('chunks_created', '?')} مقطع)"
                        )
                        st.rerun()
                    except Exception as exc:
                        st.error(f"❌ فشل الرفع: {exc}")

    st.divider()

    # ── List documents ──────────────────────────────────────────────────────
    st.subheader("المستندات المفهرسة")

    try:
        docs = list_documents()
    except Exception as exc:
        st.error(f"تعذّر تحميل قائمة المستندات: {exc}")
        docs = []

    if not docs:
        st.info("لا توجد مستندات مرفوعة بعد. ارفع ملفاً للبدء.")
    else:
        for doc in docs:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3, 1, 2, 1])
                c1.markdown(f"**{doc['filename']}**")
                c2.caption(f"{doc.get('chunks', 0)} مقطع")
                c3.caption(doc.get("uploaded_at", "")[:19].replace("T", " "))
                if c4.button("🗑️", key=f"del_{doc['doc_id']}", help="حذف المستند"):
                    with st.spinner("جاري الحذف…"):
                        try:
                            delete_document(doc["doc_id"])
                            st.success("تم حذف المستند.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"فشل الحذف: {exc}")
