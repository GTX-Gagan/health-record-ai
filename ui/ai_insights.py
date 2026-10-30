import streamlit as st

from database.models import Patient


def render_ai_insights(session) -> None:
    st.header("AI health insights")
    st.info("These are AI-generated health-risk indications, not medical diagnoses. Consult a qualified clinician for medical advice.")
    patients = session.query(Patient).order_by(Patient.updated_at.desc()).all()
    for patient in patients:
        st.subheader(patient.full_name)
        if patient.ai_status == "completed":
            st.code(patient.remarks or "", language="json")
        else:
            st.warning(patient.ai_error or "AI analysis is pending.")
