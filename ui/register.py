"""Patient registration view for Health Record AI.

Provides the clinical enrollment interface with structured guidance,
responsive form centering to prevent overflow, and detailed notification feedback.
Includes an in-flight submission guard to prevent repeated rapid submissions.
"""

from __future__ import annotations

import streamlit as st

from exceptions import ApplicationError, DuplicatePatientError, ValidationError
from ui.components import patient_form


def render_register(service, *args, **kwargs) -> None:
    st.markdown(
        """
        <div style="margin-bottom: 1.75rem;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.35rem;">
                <span class="saas-badge saas-badge-info">Clinical Intake</span>
                <span class="saas-badge saas-badge-neutral">SQLAlchemy Enforced</span>
            </div>
            <h1 style="font-size: 1.85rem; margin: 0.25rem 0 0.35rem 0;">Register New Patient</h1>
            <p style="color: #64748b; font-size: 0.96rem; margin: 0; max-width: 720px;">
                Enter verified patient demographics and diagnostic blood measurements. Records are validated with Pydantic v2 schemas and persisted securely to the database.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Initialize submission guard in session state
    if "is_submitting" not in st.session_state:
        st.session_state.is_submitting = False

    # Center the form layout to prevent horizontal stretching and eliminate overflow
    col_left_spacer, col_content, col_right_spacer = st.columns([1, 14, 1])

    with col_content:
        data = patient_form(key="register_patient_form", submit_label="Save Patient Record")
        if data:
            if st.session_state.is_submitting:
                st.warning("⚠️ Patient registration is currently being processed. Please wait.")
                return

            st.session_state.is_submitting = True
            try:
                with st.spinner("Persisting patient record and connecting to AI screening service..."):
                    patient = service.create(data)

                st.markdown(
                    f"""
                    <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 12px; padding: 1.25rem; margin-top: 1rem;">
                        <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #065f46; font-size: 1.05rem;">
                            <span>✅</span> Patient Record Successfully Enrolled
                        </div>
                        <p style="color: #047857; margin: 0.5rem 0 0.25rem 0; font-size: 0.92rem;">
                            Record for <strong>{patient.full_name}</strong> (DOB: {patient.date_of_birth:%d/%m/%Y}, Email: {patient.email}) has been saved to the database.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if patient.ai_status == "completed":
                    st.info("🧬 Preliminary AI health screening analysis generated and attached to record.")
                else:
                    st.caption(
                        "ℹ️ AI analysis status: Pending / Offline. Upstream Gemini API is currently unavailable; "
                        "the patient record is safely preserved and can be re-analyzed from the Patient Records page."
                    )
            except ValidationError as exc:
                st.error(f"Validation Failed: {exc}")
            except DuplicatePatientError as exc:
                st.warning(f"Duplicate Identity Detected: {exc}")
            except ApplicationError as exc:
                st.error(str(exc))
            finally:
                st.session_state.is_submitting = False
