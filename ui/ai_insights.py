"""Clinical AI health insights view for Health Record AI.

Provides structured presentation of Gemini-generated health-risk screening
summaries, explicit clinical disclaimers, clear distinction between successful,
pending, and failed analyses, and graceful handling of upstream API outages.
"""

from __future__ import annotations

import json
import time
from sqlalchemy import select
import streamlit as st

from database.models import Patient
from exceptions import ApplicationError
from services.ai_service import format_ai_error


def _handle_retry(patient_id: int, service) -> None:
    now = time.time()
    last_retry = st.session_state.get(f"retry_cooldown_insight_{patient_id}", 0.0)
    if now - last_retry < 15:
        remaining = int(15 - (now - last_retry))
        st.warning(f"⏳ Free-tier quota cooling down. Please wait {remaining}s before re-attempting AI screening.")
    else:
        st.session_state[f"retry_cooldown_insight_{patient_id}"] = now
        try:
            with st.spinner("Connecting to Gemini AI Service (Free Tier)..."):
                updated_patient = service.retry_ai(patient_id)
            if updated_patient and updated_patient.ai_status == "completed":
                st.success("AI screening completed successfully.")
            else:
                retry_err = format_ai_error(updated_patient.ai_error if updated_patient else None)
                st.warning(retry_err)
            st.rerun()
        except ApplicationError as exc:
            st.error(f"Retry request failed: {format_ai_error(str(exc))}")


def render_ai_insights(session, service=None) -> None:
    # Support flexible caller signatures (session, service or service alone)
    if hasattr(session, "repository") and hasattr(session.repository, "session"):
        service = session
        session = service.repository.session
    elif service is None and hasattr(session, "scalars"):
        try:
            from config.settings import get_settings
            from database.repository import PatientRepository
            from services.ai_service import GeminiAIService
            from services.patient_service import PatientService

            service = PatientService(PatientRepository(session), GeminiAIService(get_settings()))
        except Exception:
            service = None

    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.35rem;">
                <span class="saas-badge saas-badge-info">Google GenAI Free Tier</span>
                <span class="saas-badge saas-badge-neutral">Clinical Triage Support</span>
            </div>
            <h1 style="font-size: 1.85rem; margin: 0.25rem 0 0.35rem 0;">Clinical AI Health Insights</h1>
            <p style="color: #64748b; font-size: 0.96rem; margin: 0;">
                Automated preliminary biomarker risk stratification powered by Google Gemini (Free Tier).
            </p>
        </div>

        <div class="clinical-disclaimer">
            <span style="font-size: 1.25rem;">🩺</span>
            <div>
                <strong>Clinical Advisory & Non-Diagnostic Notice:</strong><br>
                AI-generated remarks are preliminary health-risk indications designed solely for administrative triage.
                They do not constitute a medical diagnosis or treatment plan. All clinical findings must be evaluated by a qualified clinician.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    patients = list(session.scalars(select(Patient).order_by(Patient.updated_at.desc())))

    if not patients:
        st.info("No patient records registered yet. Register a patient to initiate clinical screening.")
        return

    completed_count = sum(1 for p in patients if p.ai_status == "completed")
    pending_count = sum(1 for p in patients if p.ai_status == "pending")
    failed_count = sum(1 for p in patients if p.ai_status == "failed")

    # Metric Counter Banner - Clearly distinguishes Completed, Pending, and Failed
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="saas-card" style="padding: 0.9rem 1.1rem; margin-bottom: 1rem;">
                <div style="font-size: 0.76rem; color: #64748b; font-weight: 600; text-transform: uppercase;">Total Patients</div>
                <div style="font-size: 1.55rem; font-weight: 800; color: #0f172a; margin: 4px 0;">{len(patients)}</div>
                <div style="font-size: 0.78rem; color: #64748b;">Enrolled Cohort</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="saas-card" style="padding: 0.9rem 1.1rem; margin-bottom: 1rem;">
                <div style="font-size: 0.76rem; color: #059669; font-weight: 600; text-transform: uppercase;">AI Completed</div>
                <div style="font-size: 1.55rem; font-weight: 800; color: #059669; margin: 4px 0;">{completed_count}</div>
                <div style="font-size: 0.78rem; color: #059669;">Verified Screenings</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="saas-card" style="padding: 0.9rem 1.1rem; margin-bottom: 1rem;">
                <div style="font-size: 0.76rem; color: #475569; font-weight: 600; text-transform: uppercase;">AI Pending</div>
                <div style="font-size: 1.55rem; font-weight: 800; color: #334155; margin: 4px 0;">{pending_count}</div>
                <div style="font-size: 0.78rem; color: #64748b;">In Processing Queue</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="saas-card" style="padding: 0.9rem 1.1rem; margin-bottom: 1rem;">
                <div style="font-size: 0.76rem; color: #d97706; font-weight: 600; text-transform: uppercase;">Quota / Failed</div>
                <div style="font-size: 1.55rem; font-weight: 800; color: #d97706; margin: 4px 0;">{failed_count}</div>
                <div style="font-size: 0.78rem; color: #d97706;">Awaiting Retry</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Detect if any patient has quota exhaustion to show ONE compact summary banner
    has_quota_exhausted = any(
        p.ai_status == "failed"
        and (
            "limit reached" in format_ai_error(p.ai_error).lower()
            or "quota" in format_ai_error(p.ai_error).lower()
            or "429" in str(p.ai_error).upper()
            or "RESOURCE_EXHAUSTED" in str(p.ai_error).upper()
        )
        for p in patients
    )

    if has_quota_exhausted:
        st.markdown(
            """
            <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px; padding: 0.85rem 1.15rem; margin-bottom: 1.25rem; display: flex; align-items: flex-start; gap: 12px; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);">
                <span style="font-size: 1.25rem; line-height: 1.2;">⚠️</span>
                <div style="flex: 1;">
                    <div style="font-weight: 700; color: #92400e; font-size: 0.92rem; margin-bottom: 2px;">
                        Gemini Free-Tier Quota Temporarily Exhausted
                    </div>
                    <div style="color: #78350f; font-size: 0.86rem; line-height: 1.45;">
                        Gemini free-tier request limit reached. Please try again after the quota resets.
                        In strict compliance with clinical integrity guidelines, <strong>no synthetic or fabricated AI output has been generated</strong>.
                        Patient laboratory biomarkers remain safely persisted in the database and can be evaluated on demand via the retry buttons below.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif failed_count > 0:
        st.markdown(
            """
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.85rem 1.15rem; margin-bottom: 1.25rem; display: flex; align-items: flex-start; gap: 12px; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);">
                <span style="font-size: 1.25rem; line-height: 1.2;">ℹ️</span>
                <div style="flex: 1;">
                    <div style="font-weight: 700; color: #1e293b; font-size: 0.92rem; margin-bottom: 2px;">
                        AI Screening Status Advisory
                    </div>
                    <div style="color: #475569; font-size: 0.86rem; line-height: 1.45;">
                        Some patient records currently require screening. Zero synthetic predictions are fabricated.
                        Use the single retry button on individual cards to initiate or re-run analysis.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # Render Patient Triage Dossiers in compact, consistent cards
    for patient in patients:
        with st.container(border=True):
            # Clearly distinguish status badge
            if patient.ai_status == "completed":
                badge_html = '<span class="saas-badge saas-badge-success">● Screening Ready</span>'
            elif patient.ai_status == "pending":
                badge_html = '<span class="saas-badge saas-badge-neutral">● Screening Pending</span>'
            else:
                err_clean = format_ai_error(patient.ai_error)
                if "limit reached" in err_clean.lower() or "quota" in err_clean.lower():
                    badge_html = '<span class="saas-badge saas-badge-warning">● Quota Limit</span>'
                else:
                    badge_html = '<span class="saas-badge saas-badge-error">● AI Failed</span>'

            st.markdown(
                f"""
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                    <div>
                        <span style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">#{patient.id:03d} · {patient.full_name}</span>
                        <span style="color: #64748b; font-size: 0.84rem; margin-left: 8px;">(DOB: {patient.date_of_birth:%d/%m/%Y})</span>
                    </div>
                    <div>
                        {badge_html}
                    </div>
                </div>
                <div style="display: flex; gap: 16px; margin-bottom: 0.5rem; font-size: 0.86rem; color: #475569;">
                    <span>🧪 Glucose: <strong>{patient.glucose} mg/dL</strong></span>
                    <span>🩸 Haemoglobin: <strong>{patient.haemoglobin} g/dL</strong></span>
                    <span>🫀 Cholesterol: <strong>{patient.cholesterol} mg/dL</strong></span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # 1. COMPLETED STATUS
            if patient.ai_status == "completed" and patient.remarks:
                try:
                    remark_data = json.loads(patient.remarks)
                except Exception:
                    remark_data = None

                if remark_data:
                    risk_level = str(remark_data.get("risk", "Screened")).strip().capitalize()
                    explanation = remark_data.get("explanation", "Screening completed.")
                    possible_risks = remark_data.get("possible_risks", [])
                    next_steps = remark_data.get("next_steps", [])

                    st.markdown(
                        f"""
                        <div style="background: #f0fdfa; border: 1px solid #99f6e4; border-radius: 8px; padding: 0.85rem 1.1rem; margin: 0.4rem 0 0.6rem 0;">
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.4rem;">
                                <div style="font-weight: 700; color: #0f766e; font-size: 0.92rem;">
                                    Stratified Risk Category: <span class="saas-badge saas-badge-info">{risk_level}</span>
                                </div>
                                <span style="font-size: 0.78rem; color: #0f766e;">Model: {patient.ai_model or 'gemini-flash'}</span>
                            </div>
                            <p style="color: #134e4a; font-size: 0.88rem; margin: 0 0 0.4rem 0;">{explanation}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    c_risk, c_steps = st.columns(2)
                    with c_risk:
                        st.markdown("**Identified Risk Factors:**")
                        for item in possible_risks:
                            st.markdown(f"- {item}")
                    with c_steps:
                        st.markdown("**Recommended Clinical Next Steps:**")
                        for item in next_steps:
                            st.markdown(f"- {item}")

                with st.expander("📄 Structured AI Response (JSON Payload)", expanded=False):
                    st.code(patient.remarks, language="json")

            # 2. PENDING STATUS
            elif patient.ai_status == "pending":
                st.markdown(
                    """
                    <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px; padding: 0.65rem 0.95rem; margin: 0.25rem 0 0.6rem 0; font-size: 0.86rem; color: #475569; display: flex; align-items: center; justify-content: space-between;">
                        <span>⏳ <strong>Status:</strong> AI screening queued or awaiting processing.</span>
                        <span style="color: #64748b; font-size: 0.78rem;">Zero synthetic data generated</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if service is not None:
                    if st.button("⚡  Run AI Screening", key=f"ai_retry_btn_{patient.id}", type="secondary"):
                        _handle_retry(patient.id, service)

            # 3. FAILED STATUS (e.g. Quota Exhaustion or Network Error)
            else:
                user_friendly_error = format_ai_error(patient.ai_error)
                st.markdown(
                    f"""
                    <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 0.65rem 0.95rem; margin: 0.25rem 0 0.6rem 0; font-size: 0.86rem; color: #92400e; display: flex; align-items: center; justify-content: space-between;">
                        <span>⚠️ <strong>Notice:</strong> {user_friendly_error}</span>
                        <span style="color: #b45309; font-size: 0.78rem;">Vitals safe in database</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                # Exactly one retry button per patient
                if service is not None:
                    if st.button("🔄  Retry AI Screening", key=f"ai_retry_btn_{patient.id}", type="secondary"):
                        _handle_retry(patient.id, service)
