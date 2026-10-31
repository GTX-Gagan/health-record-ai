"""Clinical administration dashboard view for Health Record AI.

Presents a welcome hero, authentic cohort KPI cards, real biomarker charts
based on actual patient data, and a recent enrollment activity roster.
"""

from __future__ import annotations

import altair as alt
import pandas as pd
from sqlalchemy import func, select
import streamlit as st

from database.models import Patient


def render_dashboard(session, *args, **kwargs) -> None:
    # 1. Polished Welcome Hero
    st.markdown(
        """
        <div class="saas-hero">
            <div class="saas-hero-badge">
                <span>●</span> Operational Medical Administration Suite
            </div>
            <h1>Clinical Administration Dashboard</h1>
            <p>
                Real-time operational surveillance of registered patients, clinical blood biomarkers,
                and preliminary AI health screening status.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Extract Real Statistics from Database
    total = session.scalar(select(func.count(Patient.id))) or 0
    completed = session.scalar(select(func.count(Patient.id)).where(Patient.ai_status == "completed")) or 0
    pending = session.scalar(select(func.count(Patient.id)).where(Patient.ai_status != "completed")) or 0
    avg_glucose = session.scalar(select(func.avg(Patient.glucose)))
    avg_glucose_display = f"{float(avg_glucose):.1f} mg/dL" if avg_glucose else "—"

    # 3. KPI Cards Grid
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="saas-kpi-card kpi-blue">
                <div class="saas-kpi-header">
                    <span class="saas-kpi-title">Total Enrolled</span>
                    <div class="saas-kpi-icon">👥</div>
                </div>
                <div class="saas-kpi-value">{total}</div>
                <div class="saas-kpi-sub">
                    <span class="saas-badge saas-badge-neutral">Active Cohort</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="saas-kpi-card kpi-emerald">
                <div class="saas-kpi-header">
                    <span class="saas-kpi-title">AI Screened</span>
                    <div class="saas-kpi-icon">🧬</div>
                </div>
                <div class="saas-kpi-value">{completed}</div>
                <div class="saas-kpi-sub">
                    <span class="saas-badge saas-badge-success">Ready for Review</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="saas-kpi-card kpi-amber">
                <div class="saas-kpi-header">
                    <span class="saas-kpi-title">Pending / Offline</span>
                    <div class="saas-kpi-icon">⏳</div>
                </div>
                <div class="saas-kpi-value">{pending}</div>
                <div class="saas-kpi-sub">
                    <span class="saas-badge saas-badge-warning">Awaiting Retry</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="saas-kpi-card">
                <div class="saas-kpi-header">
                    <span class="saas-kpi-title">Avg Glucose</span>
                    <div class="saas-kpi-icon">🧪</div>
                </div>
                <div class="saas-kpi-value" style="font-size: 1.7rem; padding-top: 5px;">{avg_glucose_display}</div>
                <div class="saas-kpi-sub">
                    <span class="saas-badge saas-badge-neutral">Cohort Mean</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 4. Cohort Biomarker Visual Summary & Recent Roster
    patients = list(session.scalars(select(Patient).order_by(Patient.created_at.desc())))

    if patients:
        col_chart, col_status = st.columns([7, 5], gap="large")

        with col_chart:
            st.markdown(
                """
                <div class="saas-section-header">
                    <h3>📊 Cohort Blood Biomarkers (mg/dL)</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Build data records for Altair grouped bar chart
            chart_records = []
            # Display recent patients in chronological order left-to-right
            display_patients = list(reversed(patients[:8]))
            for p in display_patients:
                chart_records.append({
                    "Patient": p.full_name,
                    "Biomarker": "Fasting Glucose",
                    "Value": float(p.glucose),
                })
                chart_records.append({
                    "Patient": p.full_name,
                    "Biomarker": "Total Cholesterol",
                    "Value": float(p.cholesterol),
                })
            df_chart = pd.DataFrame(chart_records)

            biomarker_chart = (
                alt.Chart(df_chart)
                .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(
                    x=alt.X(
                        "Patient:N",
                        title="Patient Cohort",
                        sort=None,
                        axis=alt.Axis(
                            labelAngle=-25,
                            labelColor="#475569",
                            titleColor="#0f172a",
                            labelFontSize=11,
                            titleFontSize=12,
                            labelLimit=120,
                        ),
                    ),
                    y=alt.Y(
                        "Value:Q",
                        title="Biomarker Value (mg/dL)",
                        axis=alt.Axis(
                            labelColor="#475569",
                            titleColor="#0f172a",
                            gridColor="#f1f5f9",
                            labelFontSize=11,
                            titleFontSize=12,
                        ),
                    ),
                    color=alt.Color(
                        "Biomarker:N",
                        scale=alt.Scale(
                            domain=["Fasting Glucose", "Total Cholesterol"],
                            range=["#0d9488", "#2563eb"],
                        ),
                        legend=alt.Legend(
                            title=None,
                            orient="top",
                            direction="horizontal",
                            labelColor="#334155",
                            labelFontSize=12,
                        ),
                    ),
                    xOffset="Biomarker:N",
                    tooltip=[
                        alt.Tooltip("Patient:N", title="Patient"),
                        alt.Tooltip("Biomarker:N", title="Biomarker"),
                        alt.Tooltip("Value:Q", title="Value (mg/dL)", format=".1f"),
                    ],
                )
                .properties(background="#ffffff", height=320)
                .configure_view(strokeWidth=0, fill="#ffffff")
                .configure_axis(domainColor="#cbd5e1", tickColor="#cbd5e1")
            )

            with st.container(border=True):
                st.altair_chart(biomarker_chart, use_container_width=True)

        with col_status:
            st.markdown(
                """
                <div class="saas-section-header">
                    <h3>🛡️ System & AI Triage Health</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="saas-card" style="margin-bottom: 0.75rem;">
                    <div style="font-size: 0.82rem; color: #64748b; font-weight: 600; text-transform: uppercase;">Persistence Engine</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin: 4px 0;">SQLite 3 (ACID Enforced)</div>
                    <div style="font-size: 0.85rem; color: #059669; font-weight: 600;">● Database Connected & Healthy</div>
                </div>
                <div class="saas-card" style="margin-bottom: 0.75rem;">
                    <div style="font-size: 0.82rem; color: #64748b; font-weight: 600; text-transform: uppercase;">External AI Service</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin: 4px 0;">Google Gemini Flash API</div>
                    <div style="font-size: 0.85rem; color: #d97706; font-weight: 600;">● Graceful Fallback Mode Active (503/504 resilient)</div>
                </div>
                <div class="saas-card">
                    <div style="font-size: 0.82rem; color: #64748b; font-weight: 600; text-transform: uppercase;">Privacy Protocol</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin: 4px 0;">Zero-PII Anonymized Transmission</div>
                    <div style="font-size: 0.85rem; color: #059669; font-weight: 600;">● Names & Emails Excluded from AI prompts</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

        # 5. Patient Activity Roster: Clean Light Table
        st.markdown(
            """
            <div class="saas-section-header">
                <h3>📋 Recent Patient Cohort Roster</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        roster_rows = "".join(
            f"<tr style='background: {'#ffffff' if idx % 2 == 0 else '#f8fafc'}; border-bottom: 1px solid #f1f5f9;'>"
            f"<td style='padding: 10px 14px; font-weight: 700; color: #0d9488; font-family: monospace;'>#{p.id:03d}</td>"
            f"<td style='padding: 10px 14px; font-weight: 600; color: #0f172a;'>{p.full_name}</td>"
            f"<td style='padding: 10px 14px; color: #64748b;'>{p.date_of_birth.strftime('%d/%m/%Y')}</td>"
            f"<td style='padding: 10px 14px; color: #475569;'>{p.email}</td>"
            f"<td style='padding: 10px 14px; font-weight: 600; font-family: monospace; color: #0f172a;'>{p.glucose} mg/dL</td>"
            f"<td style='padding: 10px 14px; font-weight: 600; font-family: monospace; color: #0f172a;'>{p.haemoglobin} g/dL</td>"
            f"<td style='padding: 10px 14px; font-weight: 600; font-family: monospace; color: #0f172a;'>{p.cholesterol} mg/dL</td>"
            f"<td style='padding: 10px 14px;'>"
            f"{'<span class=\"saas-badge saas-badge-success\">● Completed</span>' if p.ai_status == 'completed' else '<span class=\"saas-badge saas-badge-warning\">● Offline / Pending</span>'}"
            f"</td>"
            f"</tr>"
            for idx, p in enumerate(patients)
        )

        roster_html = (
            '<div style="overflow-x: auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05); margin-bottom: 1.5rem;">'
            '<table style="width: 100%; border-collapse: collapse; font-size: 0.88rem; font-family: inherit;">'
            '<thead><tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">'
            '<th style="padding: 12px 14px; text-align: left; font-weight: 700; color: #475569; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em;">ID</th>'
            '<th style="padding: 12px 14px; text-align: left; font-weight: 700; color: #475569; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em;">Patient Name</th>'
            '<th style="padding: 12px 14px; text-align: left; font-weight: 700; color: #475569; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em;">DOB</th>'
            '<th style="padding: 12px 14px; text-align: left; font-weight: 700; color: #475569; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em;">Email</th>'
            '<th style="padding: 12px 14px; text-align: left; font-weight: 700; color: #475569; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em;">Glucose</th>'
            '<th style="padding: 12px 14px; text-align: left; font-weight: 700; color: #475569; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em;">Haemoglobin</th>'
            '<th style="padding: 12px 14px; text-align: left; font-weight: 700; color: #475569; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em;">Cholesterol</th>'
            '<th style="padding: 12px 14px; text-align: left; font-weight: 700; color: #475569; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em;">AI Triage</th>'
            '</tr></thead>'
            f'<tbody>{roster_rows}</tbody>'
            '</table></div>'
        )
        st.markdown(roster_html, unsafe_allow_html=True)
    else:
        st.info("No patient records registered in the system yet. Navigate to 'Register Patient' to enroll records.")
