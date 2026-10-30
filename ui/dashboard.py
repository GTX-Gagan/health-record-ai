import streamlit as st
from sqlalchemy import func, select

from database.models import Patient


def render_dashboard(session) -> None:
    st.markdown('<div class="hero"><h1>Health Record AI</h1><p>Clearer patient records. Responsible AI-assisted insights.</p></div>', unsafe_allow_html=True)
    total = session.scalar(select(func.count(Patient.id))) or 0
    completed = session.scalar(select(func.count(Patient.id)).where(Patient.ai_status == "completed")) or 0
    pending = session.scalar(select(func.count(Patient.id)).where(Patient.ai_status != "completed")) or 0
    cols = st.columns(3)
    for col, label, value in zip(cols, ("Total patients", "AI analyses completed", "Pending or failed"), (total, completed, pending)):
        col.markdown(f'<div class="metric-card"><small>{label}</small><h2>{value}</h2></div>', unsafe_allow_html=True)
