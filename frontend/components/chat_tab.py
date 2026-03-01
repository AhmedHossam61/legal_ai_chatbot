"""
Chat Tab – conversational interface with the Legal AI.
Supports multi-turn conversation and optional RAG source display.
"""

import streamlit as st
from components.api_client import chat


def render_chat_tab() -> None:
    # ── Initialise session state ────────────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    messages: list[dict] = st.session_state["messages"]

    # ── Display conversation history ────────────────────────────────────────
    for msg in messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "⚖️"):
            st.markdown(msg["content"])

            # Show RAG sources if present
            if msg["role"] == "assistant" and msg.get("sources") and st.session_state.get("show_sources"):
                with st.expander(f"📚 المصادر ({len(msg['sources'])} مقطع)"):
                    for i, src in enumerate(msg["sources"], 1):
                        st.markdown(f"**[{i}] {src['source']}**")
                        st.caption(src["content"][:400] + ("…" if len(src["content"]) > 400 else ""))
                        st.divider()

    # ── User input ──────────────────────────────────────────────────────────
    prompt = st.chat_input("اكتب سؤالك القانوني هنا…", key="chat_input")

    if prompt:
        # Append user message
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Call API
        with st.chat_message("assistant", avatar="⚖️"):
            with st.spinner("جاري التحليل…"):
                try:
                    # Build history in the format the API expects
                    api_history = [
                        {"role": m["role"], "content": m["content"]}
                        for m in messages[:-1]         # exclude the current user message
                        if m["role"] in ("user", "assistant")
                    ]
                    result = chat(
                        message=prompt,
                        history=api_history,
                        use_rag=st.session_state.get("use_rag", True),
                    )
                    answer = result.get("answer", "لم أتمكن من الإجابة.")
                    sources = result.get("sources", [])

                    st.markdown(answer)

                    if sources and st.session_state.get("show_sources"):
                        with st.expander(f"📚 المصادر ({len(sources)} مقطع)"):
                            for i, src in enumerate(sources, 1):
                                st.markdown(f"**[{i}] {src['source']}**")
                                st.caption(src["content"][:400] + ("…" if len(src["content"]) > 400 else ""))
                                st.divider()

                    messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    })

                except Exception as exc:
                    err_msg = f"❌ خطأ في الاتصال بالخادم: {exc}"
                    st.error(err_msg)
                    messages.append({"role": "assistant", "content": err_msg, "sources": []})

        # Persist updated messages
        st.session_state["messages"] = messages
