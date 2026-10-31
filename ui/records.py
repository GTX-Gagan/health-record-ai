"""Patient records management view for Health Record AI.

Provides clinical search, a cohort summary table, detailed patient cards with
biomarker vitals, AI screening results, retry actions, and protected edit/delete operations.
"""

from __future__ import annotations

import time
import streamlit as st

from exceptions import ApplicationError, DuplicatePatientError, ValidationError
from services.ai_service import format_ai_error
from ui.components import patient_form


def render_records(service, repository=None, *args, **kwargs) -> None:
    if repository is None and hasattr(service, "repository"):
        repository = service.repository

    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.35rem;">
                <span class="saas-badge saas-badge-neutral">Clinical Directory</span>
                <span class="saas-badge saas-badge-info">Search & CRUD</span>
            </div>
            <h1 style="font-size: 1.85rem; margin: 0.25rem 0 0.35rem 0;">Patient Health Records</h1>
            <p style="color: #64748b; font-size: 0.96rem; margin: 0;">
                Comprehensive patient roster with laboratory biomarkers, AI screening triage, and record management.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Search Bar & Filter Controls
    search_col, count_col = st.columns([8, 3], gap="medium")
    with search_col:
        search_term = st.text_input(
            "Search",
            placeholder="🔍 Search patients by full name or email...",
            label_visibility="collapsed",
        )

    patients = repository.list(search_term)

    with count_col:
        st.markdown(
            f"""
            <div style="text-align: right; padding-top: 0.4rem; color: #64748b; font-size: 0.9rem; font-weight: 600;">
                Showing <span style="color: #0d9488;">{len(patients)}</span> patient record{"s" if len(patients) != 1 else ""}
            </div>
            """,
            unsafe_allow_html=True,
        )

    if not patients:
        st.markdown(
            """
            <div class="saas-card" style="text-align: center; padding: 3rem 1.5rem;">
                <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">🔍</div>
                <h3 style="color: #0f172a; margin-bottom: 0.25rem;">No matching patient records found</h3>
                <p style="color: #64748b; margin: 0;">Try adjusting your search criteria or register a new patient.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Master Table View: Clean Light-themed SaaS Data Table with subtle borders & readable text
    table_rows = "".join(
        f"<tr style='background-color: {'#ffffff' if idx % 2 == 0 else '#f8fafc'}; border-bottom: 1px solid #f1f5f9;'>"
        f"<td style='padding: 12px 16px; font-weight: 700; color: #0d9488; font-family: monospace; background-color: inherit;'>#{p.id:03d}</td>"
        f"<td style='padding: 12px 16px; font-weight: 600; color: #0f172a; background-color: inherit;'>{p.full_name}</td>"
        f"<td style='padding: 12px 16px; color: #64748b; background-color: inherit;'>{p.date_of_birth.strftime('%d/%m/%Y')}</td>"
        f"<td style='padding: 12px 16px; color: #475569; background-color: inherit;'>{p.email}</td>"
        f"<td style='padding: 12px 16px; font-weight: 600; font-family: monospace; color: #0f172a; background-color: inherit;'>{p.glucose} mg/dL</td>"
        f"<td style='padding: 12px 16px; font-weight: 600; font-family: monospace; color: #0f172a; background-color: inherit;'>{p.haemoglobin} g/dL</td>"
        f"<td style='padding: 12px 16px; font-weight: 600; font-family: monospace; color: #0f172a; background-color: inherit;'>{p.cholesterol} mg/dL</td>"
        f"<td style='padding: 12px 16px; background-color: inherit;'>"
        f"{'<span class=\"saas-badge saas-badge-success\">● Completed</span>' if p.ai_status == 'completed' else '<span class=\"saas-badge saas-badge-warning\">● Offline / Pending</span>'}"
        f"</td>"
        f"</tr>"
        for idx, p in enumerate(patients)
    )

    table_html = (
        '<div style="overflow-x: auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05); margin-bottom: 1.75rem;">'
        '<table class="saas-table" style="width: 100%; border-collapse: collapse; background-color: #ffffff; margin: 0; font-size: 0.9rem;">'
        '<thead><tr style="background-color: #f8fafc; border-bottom: 1px solid #e2e8f0;">'
        '<th style="padding: 12px 16px; text-align: left; font-weight: 700; color: #475569; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; background-color: #f8fafc;">ID</th>'
        '<th style="padding: 12px 16px; text-align: left; font-weight: 700; color: #475569; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; background-color: #f8fafc;">Full Name</th>'
        '<th style="padding: 12px 16px; text-align: left; font-weight: 700; color: #475569; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; background-color: #f8fafc;">DOB</th>'
        '<th style="padding: 12px 16px; text-align: left; font-weight: 700; color: #475569; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; background-color: #f8fafc;">Email</th>'
        '<th style="padding: 12px 16px; text-align: left; font-weight: 700; color: #475569; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; background-color: #f8fafc;">Glucose</th>'
        '<th style="padding: 12px 16px; text-align: left; font-weight: 700; color: #475569; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; background-color: #f8fafc;">Haemoglobin</th>'
        '<th style="padding: 12px 16px; text-align: left; font-weight: 700; color: #475569; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; background-color: #f8fafc;">Cholesterol</th>'
        '<th style="padding: 12px 16px; text-align: left; font-weight: 700; color: #475569; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; background-color: #f8fafc;">AI Triage</th>'
        '</tr></thead>'
        f'<tbody>{table_rows}</tbody>'
        '</table></div>'
    )
    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="saas-section-header">
            <h3>📂 Detailed Patient Dossiers</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Detailed Patient Cards / Expanders
    for patient in patients:
        status_badge = (
            '<span class="saas-badge saas-badge-success">● AI Ready</span>'
            if patient.ai_status == "completed"
            else '<span class="saas-badge saas-badge-warning">● AI Offline</span>'
        )

        expander_title = (
            f"#{patient.id:03d} · {patient.full_name}  —  DOB: {patient.date_of_birth:%d/%m/%Y}  |  {patient.email}"
        )

        with st.expander(expander_title, expanded=False):
            # 1. Biomarkers Header Cards
            v1, v2, v3, v4 = st.columns(4, gap="small")
            with v1:
                st.markdown(
                    f"""
                    <div class="vital-badge">
                        <span class="vital-badge-label">Fasting Glucose</span>
                        <div class="vital-badge-value">{patient.glucose} <span class="vital-badge-unit">mg/dL</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with v2:
                st.markdown(
                    f"""
                    <div class="vital-badge">
                        <span class="vital-badge-label">Haemoglobin</span>
                        <div class="vital-badge-value">{patient.haemoglobin} <span class="vital-badge-unit">g/dL</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with v3:
                st.markdown(
                    f"""
                    <div class="vital-badge">
                        <span class="vital-badge-label">Total Cholesterol</span>
                        <div class="vital-badge-value">{patient.cholesterol} <span class="vital-badge-unit">mg/dL</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with v4:
                st.markdown(
                    f"""
                    <div class="vital-badge">
                        <span class="vital-badge-label">AI Status</span>
                        <div style="margin-top: 6px;">{status_badge}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # 2. AI Remarks & Status Notice
            if patient.remarks:
                st.markdown(
                    f"""
                    <div class="ai-triage-card">
                        <div class="ai-triage-header">
                            <span class="ai-triage-title">🧬 Clinical AI Health Screening</span>
                            <span class="saas-badge saas-badge-success">{patient.ai_model or "Gemini"}</span>
                        </div>
                        <div style="font-size: 0.8rem; color: #047857; margin-bottom: 0.5rem;">
                            Generated at {patient.ai_generated_at.strftime('%d/%m/%Y %H:%M UTC') if patient.ai_generated_at else 'N/A'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander("📄 View AI Health Risk Details (JSON)", expanded=True):
                    st.code(patient.remarks, language="json")
                st.caption("⚠️ AI-generated health risk indication only; not a medical diagnosis.")
            elif patient.ai_status == "failed":
                clean_error = format_ai_error(patient.ai_error)
                st.markdown(
                    f"""
                    <div class="ai-offline-card">
                        <div class="ai-offline-header">
                            <span>⚠️</span> AI Health Screening Offline / Pending
                        </div>
                        <p class="ai-offline-text">
                            <strong>Notice:</strong> {clean_error}
                        </p>
                        <p class="ai-offline-text" style="margin-top: 4px; font-size: 0.82rem; color: #a16207;">
                            Patient records remain safe in the database. You can retry the AI screening below once free-tier quota resets.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("🔄  Retry AI Screening Analysis", key=f"retry_{patient.id}", type="secondary"):
                    now = time.time()
                    last_retry = st.session_state.get(f"retry_cooldown_{patient.id}", 0.0)
                    if now - last_retry < 15:
                        remaining = int(15 - (now - last_retry))
                        st.warning(f"⏳ Free-tier quota cooling down. Please wait {remaining}s before re-attempting AI screening.")
                    else:
                        st.session_state[f"retry_cooldown_{patient.id}"] = now
                        try:
                            with st.spinner("Connecting to Gemini AI Service (Free Tier)..."):
                                updated = service.retry_ai(patient.id)
                            if updated and updated.ai_status == "completed":
                                st.success("AI analysis completed successfully.")
                            else:
                                retry_err = format_ai_error(updated.ai_error if updated else None)
                                st.warning(retry_err)
                            st.rerun()
                        except ApplicationError as exc:
                            st.error(f"Retry request failed: {format_ai_error(str(exc))}")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            # 3. Actions: Edit and Delete Tabs
            tab_edit, tab_delete = st.tabs(["✏️  Edit Patient Information", "🗑️  Delete Record"])

            with tab_edit:
                edit_data = patient_form(patient, key=f"edit_form_{patient.id}", submit_label="Save Changes")
                if edit_data:
                    try:
                        service.update(patient.id, edit_data)
                        st.success("Patient record updated successfully.")
                        st.rerun()
                    except ValidationError as exc:
                        st.error(f"Validation error: {exc}")
                    except DuplicatePatientError as exc:
                        st.warning(f"Duplicate error: {exc}")
                    except ApplicationError as exc:
                        st.error(str(exc))

            with tab_delete:
                with st.form(f"delete_form_{patient.id}"):
                    st.markdown(
                        f"""
                        <div style="background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                            <div style="font-weight: 700; color: #9f1239; margin-bottom: 4px;">⚠️ Permanent Deletion Warning</div>
                            <div style="font-size: 0.88rem; color: #881337;">
                                This action will permanently remove <strong>{patient.full_name}</strong> from the database.
                                This operation cannot be undone.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    confirm = st.checkbox(
                        "I confirm that I want to permanently delete this patient record",
                        key=f"confirm_delete_{patient.id}",
                    )
                    delete_clicked = st.form_submit_button("🗑️  Confirm & Delete Record", type="secondary")

                if delete_clicked:
                    if confirm:
                        service.delete(patient.id)
                        st.success(f"Record for {patient.full_name} has been deleted.")
                        st.rerun()
                    else:
                        st.warning("Please check the confirmation box before deleting.")
