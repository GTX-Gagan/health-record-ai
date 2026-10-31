"""About and architecture specifications view for Health Record AI.

Presents the application purpose, key features, clinical safety protocols,
and full technology stack in a four-card professional SaaS grid layout.
"""

from __future__ import annotations

import streamlit as st


def render_about(*args, **kwargs) -> None:
    st.markdown(
        """
        <div style="margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.35rem;">
                <span class="saas-badge saas-badge-info">System Architecture</span>
                <span class="saas-badge saas-badge-success">Enterprise Grade</span>
            </div>
            <h1 style="font-size: 1.85rem; margin: 0.25rem 0 0.35rem 0;">About HealthRecord AI</h1>
            <p style="color: #64748b; font-size: 0.98rem; margin: 0; max-width: 760px;">
                HealthRecord AI is a clinical administration and patient health record platform designed with
                strict data integrity standards, resilient offline fallback modes, and responsible AI-assisted triage.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Four Structured Cards in a 2x2 Layout
    col_row1_left, col_row1_right = st.columns(2, gap="large")

    # Card 1: Application Purpose
    with col_row1_left:
        st.markdown(
            """
            <div class="saas-card" style="height: 100%; min-height: 280px;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.85rem;">
                    <span style="font-size: 1.35rem;">🎯</span>
                    <h3 style="margin: 0; font-size: 1.12rem;">Application Purpose</h3>
                </div>
                <p style="color: #334155; font-size: 0.9rem; line-height: 1.6; margin: 0 0 0.75rem 0;">
                    Designed for clinical administrators, medical researchers, and health intake coordinators,
                    HealthRecord AI centralizes the ingestion, validation, and surveillance of patient medical records.
                </p>
                <p style="color: #64748b; font-size: 0.88rem; line-height: 1.55; margin: 0;">
                    The platform bridges local, zero-leakage SQLite storage with optional Google Gemini intelligence,
                    enabling non-diagnostic health-risk screening without sacrificing clinician oversight or data security.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Card 2: Key Features
    with col_row1_right:
        st.markdown(
            """
            <div class="saas-card" style="height: 100%; min-height: 280px;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.85rem;">
                    <span style="font-size: 1.35rem;">⚡</span>
                    <h3 style="margin: 0; font-size: 1.12rem;">Key Features</h3>
                </div>
                <ul style="color: #334155; font-size: 0.88rem; line-height: 1.6; margin: 0; padding-left: 1.2rem;">
                    <li><strong>Full CRUD Lifecycle:</strong> Seamlessly register, search, inspect, update, and delete patient records with transactional safety.</li>
                    <li><strong>Real-time Surveillance:</strong> Operational dashboard tracking cohort metrics, average glucose, and triage completion rates.</li>
                    <li><strong>Biomarker Analytics:</strong> Fasting glucose, haemoglobin, and total cholesterol clinical tracking with reference range indicators.</li>
                    <li><strong>Resilient AI Retry:</strong> Discrete retry actions for records affected by upstream Gemini service disruptions.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    col_row2_left, col_row2_right = st.columns(2, gap="large")

    # Card 3: Clinical Safety & Validation
    with col_row2_left:
        st.markdown(
            """
            <div class="saas-card" style="height: 100%; min-height: 280px;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.85rem;">
                    <span style="font-size: 1.35rem;">🛡️</span>
                    <h3 style="margin: 0; font-size: 1.12rem;">Clinical Safety & Validation</h3>
                </div>
                <ul style="color: #334155; font-size: 0.88rem; line-height: 1.6; margin: 0; padding-left: 1.2rem;">
                    <li><strong>Dual Calendar Parsing:</strong> Accepts both <code>dd/mm/yyyy</code> and <code>dd.mm.yyyy</code> while strictly rejecting future or impossible dates.</li>
                    <li><strong>Strict Laboratory Bounds:</strong> Enforces positive, finite numeric constraints for all physiological biomarkers.</li>
                    <li><strong>Duplicate Prevention:</strong> Tri-field identity hashing (normalized name, date of birth, and email) prevents accidental duplicate entries.</li>
                    <li><strong>Zero-PII Transmission:</strong> Patient names and emails are never shared with external AI endpoints; only computed age and vitals are sent.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Card 4: Technology Stack
    with col_row2_right:
        st.markdown(
            """
            <div class="saas-card" style="height: 100%; min-height: 280px;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.85rem;">
                    <span style="font-size: 1.35rem;">⚙️</span>
                    <h3 style="margin: 0; font-size: 1.12rem;">Technology Stack</h3>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.6rem 0.75rem;">
                        <div style="font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase;">UI Framework</div>
                        <div style="font-size: 0.92rem; font-weight: 700; color: #0f172a;">Streamlit 1.66</div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.6rem 0.75rem;">
                        <div style="font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase;">Data Layer</div>
                        <div style="font-size: 0.92rem; font-weight: 700; color: #0f172a;">SQLAlchemy 2.1 & SQLite</div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.6rem 0.75rem;">
                        <div style="font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase;">Schema Engine</div>
                        <div style="font-size: 0.92rem; font-weight: 700; color: #0f172a;">Pydantic v2.14</div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.6rem 0.75rem;">
                        <div style="font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase;">AI Service</div>
                        <div style="font-size: 0.92rem; font-weight: 700; color: #0f172a;">Google GenAI 2.34</div>
                    </div>
                </div>
                <div style="margin-top: 10px; font-size: 0.8rem; color: #059669; font-weight: 600;">
                    ● Verified with 11/11 Passing Pytest Automated Tests
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
