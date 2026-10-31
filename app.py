"""Health Record AI - Production Healthcare Administration Dashboard.

Entry point for the Streamlit web interface with enterprise styling,
branded clinical navigation, and unified database session management.
"""

from __future__ import annotations

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

# 1. Page Configuration
st.set_page_config(
    page_title="HealthRecord AI - Clinical Workspace",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Global SaaS Styles & Database Initialization
apply_styles()
init_db()

# 3. Sidebar Branding
st.sidebar.markdown(
    """
    <div class="sidebar-brand">
        <div class="sidebar-brand-title">
            <span style="display: flex; align-items: center; justify-content: center; width: 34px; height: 34px; background: rgba(13, 148, 136, 0.25); border: 1px solid rgba(13, 148, 136, 0.5); border-radius: 8px; font-size: 1.2rem;">🩺</span>
            <span>HealthRecord<span style="color: #2dd4bf;">AI</span></span>
        </div>
        <div class="sidebar-brand-sub">Clinical Administration Suite</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 4. Branded Navigation Menu
PAGES = [
    "Dashboard",
    "Register Patient",
    "Patient Records",
    "AI Health Insights",
    "About",
]

PAGE_LABELS = {
    "Dashboard": "📊  Dashboard",
    "Register Patient": "➕  Register Patient",
    "Patient Records": "📁  Patient Records",
    "AI Health Insights": "🧬  AI Health Insights",
    "About": "ℹ️  System & About",
}

page = st.sidebar.radio(
    "Navigation",
    PAGES,
    format_func=lambda p: PAGE_LABELS.get(p, p),
    label_visibility="collapsed",
)

# 5. Sidebar System Status Footer
st.sidebar.markdown(
    """
    <div class="sidebar-footer">
        <div class="sidebar-status-pill">
            <span style="color: #94a3b8;">Database Engine</span>
            <span style="color: #34d399; font-weight: 600;">● SQLite Active</span>
        </div>
        <div class="sidebar-status-pill">
            <span style="color: #94a3b8;">AI Protocol</span>
            <span style="color: #38bdf8; font-weight: 600;">● Zero-PII Triage</span>
        </div>
        <div style="text-align: center; margin-top: 0.85rem; color: #64748b; font-size: 0.73rem; letter-spacing: 0.02em;">
            HealthRecord AI · v2.1 Enterprise
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 6. Session Lifecycle & Page Routing
with SessionLocal() as session:
    repository = PatientRepository(session)
    service = PatientService(repository, GeminiAIService(get_settings()))

    if page == "Dashboard":
        render_dashboard(session)
    elif page == "Register Patient":
        render_register(service)
    elif page == "Patient Records":
        render_records(service, repository)
    elif page == "AI Health Insights":
        render_ai_insights(session, service)
    else:
        render_about()
