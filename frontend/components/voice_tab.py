"""
Voice Tab – record a voice question and receive an audio reply.
Uses the browser's audio recorder widget via streamlit-audio-recorder.
"""

import streamlit as st
from components.api_client import transcribe_audio, chat, synthesize_speech


def render_voice_tab() -> None:
    st.subheader("🎙️ التفاعل الصوتي")
    st.caption("سجّل سؤالك القانوني صوتياً وستحصل على إجابة مسموعة.")

    # ── Audio recorder ──────────────────────────────────────────────────────
    try:
        from audio_recorder_streamlit import audio_recorder
        audio_bytes = audio_recorder(
            text="اضغط للتسجيل",
            recording_color="#e74c3c",
            neutral_color="#2c3e50",
            icon_size="2x",
        )
    except ImportError:
        st.warning(
            "مكتبة التسجيل غير مثبّتة. "
            "شغّل: `pip install audio-recorder-streamlit` ثم أعد تشغيل التطبيق.\n\n"
            "بدلاً عن ذلك يمكنك رفع ملف صوتي يدوياً:"
        )
        audio_bytes = None

    # ── Fallback: file uploader ─────────────────────────────────────────────
    uploaded_audio = st.file_uploader(
        "أو ارفع ملف صوتي (WAV, MP3, M4A)",
        type=["wav", "mp3", "m4a", "webm", "ogg"],
    )

    raw_bytes = audio_bytes or (uploaded_audio.read() if uploaded_audio else None)
    fname = "audio.wav" if audio_bytes else (uploaded_audio.name if uploaded_audio else "audio.wav")

    if raw_bytes:
        st.audio(raw_bytes, format="audio/wav")

        if st.button("🔍 تفريغ وتحليل", type="primary", use_container_width=True):
            # Step 1 – ASR
            with st.spinner("جاري تحويل الصوت إلى نص…"):
                try:
                    asr_result = transcribe_audio(raw_bytes, fname)
                    transcript = asr_result.get("text", "")
                except Exception as exc:
                    st.error(f"❌ خطأ في تحويل الصوت: {exc}")
                    return

            st.success(f"**النص المُفرَّغ:** {transcript}")

            if not transcript.strip():
                st.warning("لم يتم الكشف عن كلام واضح.")
                return

            # Step 2 – LLM + RAG
            with st.spinner("جاري تحليل السؤال القانوني…"):
                try:
                    result = chat(
                        message=transcript,
                        history=[],
                        use_rag=st.session_state.get("use_rag", True),
                    )
                    answer = result.get("answer", "لم أتمكن من الإجابة.")
                except Exception as exc:
                    st.error(f"❌ خطأ في الإجابة: {exc}")
                    return

            st.markdown(f"**الإجابة:** {answer}")

            # Step 3 – TTS
            with st.spinner("جاري تحويل الإجابة إلى صوت…"):
                try:
                    audio_response = synthesize_speech(answer)
                    st.audio(audio_response, format="audio/wav")
                except Exception as exc:
                    st.warning(f"تعذّر إنشاء الصوت: {exc}")
