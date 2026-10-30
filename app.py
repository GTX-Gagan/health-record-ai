import streamlit as st

from config.settings import get_settings
from database.connection import SessionLocal, init_db
from database.repository import PatientRepository
from services.ai_service import GeminiAIService
from services.patient_service import PatientService
from ui.about import render_about
from ui.ai_insights import render_ai_insights
from ui.dashboard import render_dashboard
from ui.records import render_records
from ui.register import render_register
from ui.styles import apply_styles

st.set_page_config(page_title="Health Record AI", page_icon="🩺", layout="wide")
apply_styles()
init_db()

with SessionLocal() as session:
    repository = PatientRepository(session)
    service = PatientService(repository, GeminiAIService(get_settings()))
    page = st.sidebar.radio("Navigation", ["Dashboard", "Register Patient", "Patient Records", "AI Health Insights", "About"])
    if page == "Dashboard":
        render_dashboard(session)
    elif page == "Register Patient":
        render_register(service)
    elif page == "Patient Records":
        render_records(service, repository)
    elif page == "AI Health Insights":
        render_ai_insights(session)
    else:
        render_about()
