"""Reusable UI components for Health Record AI.

Provides the standardized patient registration and editing form structured
as two distinct white cards for Patient Information and Health Measurements,
with aligned fields, responsive column layouts, and zero horizontal clipping.
"""

from __future__ import annotations

import streamlit as st

from database.models import Patient


def patient_form(
    patient: Patient | None = None,
    key: str = "patient_form",
    submit_label: str = "Save Patient Record",
) -> dict | None:
    """Render a structured patient input form organized in two distinct cards.

    Returns the raw form input dictionary upon submission, or None if not submitted.
    """
    with st.form(key):
        # Card 1: Patient Information
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.85rem;">
                    <span style="font-size: 1.15rem;">👤</span>
                    <span style="font-weight: 700; font-size: 0.95rem; color: #0f172a; text-transform: uppercase; letter-spacing: 0.04em;">Patient Information</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            name = st.text_input(
                "Full Name *",
                value=patient.full_name if patient else "",
                placeholder="e.g. Eleanor Vance",
                help="Legal full name. Accepts letters, spaces, hyphens, and apostrophes.",
            )

            col_dob, col_email = st.columns(2, gap="medium")
            with col_dob:
                dob = st.text_input(
                    "Date of Birth *",
                    value=patient.date_of_birth.strftime("%d/%m/%Y") if patient else "",
                    placeholder="dd/mm/yyyy or dd.mm.yyyy",
                    help="Accepts dd/mm/yyyy or dd.mm.yyyy (e.g. 28/01/1960).",
                )
            with col_email:
                email = st.text_input(
                    "Email Address *",
                    value=patient.email if patient else "",
                    placeholder="patient@example.com",
                    help="Valid patient email address.",
                )

        # Card 2: Health Measurements
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.85rem;">
                    <span style="font-size: 1.15rem;">🩸</span>
                    <span style="font-weight: 700; font-size: 0.95rem; color: #0f172a; text-transform: uppercase; letter-spacing: 0.04em;">Health Measurements</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c1, c2, c3 = st.columns(3, gap="medium")
            with c1:
                glucose = st.text_input(
                    "Glucose (mg/dL) *",
                    value=str(patient.glucose) if patient else "",
                    placeholder="e.g. 95",
                    help="Fasting blood glucose level. Positive finite number.",
                )
            with c2:
                haemoglobin = st.text_input(
                    "Haemoglobin (g/dL) *",
                    value=str(patient.haemoglobin) if patient else "",
                    placeholder="e.g. 13.5",
                    help="Haemoglobin concentration. Positive finite number.",
                )
            with c3:
                cholesterol = st.text_input(
                    "Total Cholesterol (mg/dL) *",
                    value=str(patient.cholesterol) if patient else "",
                    placeholder="e.g. 180",
                    help="Serum total cholesterol. Positive finite number.",
                )

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            f"💾  {submit_label}",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        return {
            "full_name": name,
            "date_of_birth": dob,
            "email": email,
            "glucose": glucose,
            "haemoglobin": haemoglobin,
            "cholesterol": cholesterol,
        }
    return None
