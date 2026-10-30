import streamlit as st


def render_about() -> None:
    st.header("About")
    st.write("Health Record AI is a demonstration patient-record manager with SQLite persistence and optional Gemini-assisted, non-diagnostic health-risk summaries.")
    st.info("AI remarks are informational only and do not replace qualified medical advice.")
