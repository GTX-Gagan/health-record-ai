"""SaaS Design System for Health Record AI.

Provides a unified healthcare administration theme with a sophisticated navy,
teal, and soft-slate color palette, clean typography, responsive card layouts,
and rock-solid overflow prevention.
"""

from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        :root {
            --hra-navy-dark: #071526;
            --hra-navy-surface: #0c233c;
            --hra-navy-border: #1a3a5f;
            --hra-page-bg: #f8fafc;
            --hra-card-bg: #ffffff;
            --hra-card-border: #e2e8f0;
            --hra-card-hover-border: #cbd5e1;
            --hra-text-main: #0f172a;
            --hra-text-muted: #64748b;
            --hra-text-subtle: #94a3b8;
            --hra-teal: #0d9488;
            --hra-teal-dark: #0f766e;
            --hra-teal-light: #f0fdfa;
            --hra-teal-border: #ccfbf1;
            --hra-blue: #2563eb;
            --hra-blue-light: #eff6ff;
            --hra-emerald: #059669;
            --hra-emerald-light: #ecfdf5;
            --hra-amber: #d97706;
            --hra-amber-light: #fffbeb;
            --hra-rose: #e11d48;
            --hra-rose-light: #fff1f2;
            --hra-shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.05);
            --hra-shadow-md: 0 4px 12px -2px rgba(15, 23, 42, 0.06), 0 2px 6px -2px rgba(15, 23, 42, 0.04);
            --hra-shadow-lg: 0 10px 25px -3px rgba(15, 23, 42, 0.08), 0 4px 10px -4px rgba(15, 23, 42, 0.03);
            --hra-radius-sm: 8px;
            --hra-radius-md: 12px;
            --hra-radius-lg: 16px;
        }

        /* Prevent Horizontal Overflow Globally */
        html, body, [class*="stApp"], [data-testid="stAppViewContainer"] {
            overflow-x: hidden !important;
            max-width: 100vw !important;
            background-color: var(--hra-page-bg) !important;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            color: var(--hra-text-main) !important;
        }

        /* Adjust main container padding to avoid top-header clipping */
        [data-testid="stMainBlockContainer"], .block-container {
            max-width: 1140px !important;
            padding-top: 3.25rem !important;
            padding-bottom: 3.5rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            margin-left: auto !important;
            margin-right: auto !important;
            overflow-x: hidden !important;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        /* Professional Dark Navy Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #071526 0%, #0a1f36 100%) !important;
            border-right: 1px solid var(--hra-navy-border) !important;
        }

        [data-testid="stSidebar"] * {
            color: #e2e8f0 !important;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: #94a3b8 !important;
        }

        /* Sidebar Navigation Radio Buttons */
        [data-testid="stSidebar"] [data-testid="stRadio"] > div {
            gap: 6px;
        }

        [data-testid="stSidebar"] label[data-testid="stRadioOption"] {
            background: transparent;
            border-radius: var(--hra-radius-sm);
            padding: 0.6rem 0.85rem;
            margin: 2px 0;
            transition: all 0.15s ease-in-out;
            border: 1px solid transparent;
            cursor: pointer;
        }

        [data-testid="stSidebar"] label[data-testid="stRadioOption"]:hover {
            background: rgba(255, 255, 255, 0.06) !important;
            border-color: rgba(255, 255, 255, 0.08) !important;
        }

        [data-testid="stSidebar"] label[data-testid="stRadioOption"]:has(input:checked) {
            background: linear-gradient(90deg, rgba(13, 148, 136, 0.22) 0%, rgba(13, 148, 136, 0.08) 100%) !important;
            border: 1px solid rgba(13, 148, 136, 0.45) !important;
        }

        [data-testid="stSidebar"] label[data-testid="stRadioOption"]:has(input:checked) * {
            color: #5eead4 !important;
            font-weight: 600 !important;
        }

        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            color: var(--hra-text-main) !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }

        /* Reusable Card System */
        .saas-card {
            background: var(--hra-card-bg);
            border: 1px solid var(--hra-card-border);
            border-radius: var(--hra-radius-lg);
            padding: 1.5rem 1.75rem;
            box-shadow: var(--hra-shadow-sm);
            margin-bottom: 1.25rem;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }

        .saas-card:hover {
            border-color: var(--hra-card-hover-border);
            box-shadow: var(--hra-shadow-md);
        }

        /* Welcome Banner Hero */
        .saas-hero {
            background: linear-gradient(135deg, #091e3a 0%, #0d3b59 55%, #0d9488 100%);
            border-radius: var(--hra-radius-lg);
            padding: 2.25rem 2.5rem;
            color: #ffffff;
            margin-bottom: 2rem;
            box-shadow: var(--hra-shadow-lg);
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .saas-hero h1 {
            color: #ffffff !important;
            font-size: 1.95rem !important;
            font-weight: 800 !important;
            margin: 0 0 0.5rem 0 !important;
            letter-spacing: -0.03em;
        }

        .saas-hero p {
            color: #cbd5e1 !important;
            font-size: 1.05rem !important;
            margin: 0 !important;
            max-width: 680px;
            line-height: 1.5;
        }

        .saas-hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #ffffff;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.78rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Metric KPI Cards */
        .saas-kpi-card {
            background: var(--hra-card-bg);
            border: 1px solid var(--hra-card-border);
            border-radius: var(--hra-radius-md);
            padding: 1.25rem 1.4rem;
            box-shadow: var(--hra-shadow-sm);
            position: relative;
            overflow: hidden;
            transition: all 0.2s ease;
        }

        .saas-kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--hra-shadow-md);
            border-color: var(--hra-card-hover-border);
        }

        .saas-kpi-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--hra-teal);
        }

        .saas-kpi-card.kpi-blue::before { background: var(--hra-blue); }
        .saas-kpi-card.kpi-emerald::before { background: var(--hra-emerald); }
        .saas-kpi-card.kpi-amber::before { background: var(--hra-amber); }

        .saas-kpi-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }

        .saas-kpi-title {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--hra-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .saas-kpi-icon {
            width: 34px;
            height: 34px;
            border-radius: var(--hra-radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            background: var(--hra-page-bg);
        }

        .saas-kpi-value {
            font-size: 2.1rem;
            font-weight: 800;
            color: var(--hra-text-main);
            line-height: 1.1;
            margin: 0.25rem 0 0.4rem 0;
            letter-spacing: -0.02em;
        }

        .saas-kpi-sub {
            font-size: 0.82rem;
            color: var(--hra-text-muted);
            display: flex;
            align-items: center;
            gap: 4px;
        }

        /* Status Badges */
        .saas-badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 3px 10px;
            border-radius: 9999px;
            font-size: 0.76rem;
            font-weight: 600;
            line-height: 1.2;
        }

        .saas-badge-success {
            background-color: var(--hra-emerald-light);
            color: var(--hra-emerald);
            border: 1px solid #a7f3d0;
        }

        .saas-badge-warning {
            background-color: var(--hra-amber-light);
            color: var(--hra-amber);
            border: 1px solid #fde68a;
        }

        .saas-badge-error {
            background-color: var(--hra-rose-light);
            color: var(--hra-rose);
            border: 1px solid #fecdd3;
        }

        .saas-badge-info {
            background-color: var(--hra-blue-light);
            color: var(--hra-blue);
            border: 1px solid #bfdbfe;
        }

        .saas-badge-neutral {
            background-color: #f1f5f9;
            color: #475569;
            border: 1px solid #cbd5e1;
        }

        /* Section Containers */
        .saas-section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 1.5rem 0 1rem 0;
            padding-bottom: 0.6rem;
            border-bottom: 1px solid var(--hra-card-border);
        }

        .saas-section-header h3 {
            margin: 0 !important;
            font-size: 1.15rem !important;
            font-weight: 700 !important;
        }

        /* Streamlit Form Container */
        [data-testid="stForm"] {
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            padding: 0 !important;
            box-shadow: none !important;
            margin-bottom: 2rem !important;
        }

        /* Labels */
        [data-testid="stMain"] label {
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            color: #1e293b !important;
            margin-bottom: 0.35rem !important;
        }

        /* Form Inputs */
        [data-testid="stMain"] input,
        [data-testid="stMain"] textarea {
            background: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: var(--hra-radius-sm) !important;
            padding: 0.6rem 0.85rem !important;
            font-size: 0.92rem !important;
            transition: all 0.15s ease !important;
        }

        [data-testid="stMain"] input:focus,
        [data-testid="stMain"] textarea:focus {
            border-color: var(--hra-teal) !important;
            box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.18) !important;
            outline: none !important;
        }

        [data-testid="stMain"] input::placeholder {
            color: #94a3b8 !important;
            font-size: 0.88rem;
        }

        /* Primary Button */
        [data-testid="stMain"] button[kind="primary"],
        [data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, var(--hra-teal) 0%, var(--hra-teal-dark) 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: var(--hra-radius-sm) !important;
            padding: 0.75rem 1.6rem !important;
            font-size: 0.98rem !important;
            font-weight: 700 !important;
            box-shadow: 0 2px 8px rgba(13, 148, 136, 0.3) !important;
            transition: all 0.2s ease !important;
            letter-spacing: 0.02em;
        }

        [data-testid="stMain"] button[kind="primary"]:hover,
        [data-testid="stFormSubmitButton"] button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 5px 14px rgba(13, 148, 136, 0.42) !important;
            filter: brightness(1.04) !important;
        }

        /* Secondary Button */
        [data-testid="stMain"] button[kind="secondary"],
        [data-testid="stButton"] button {
            background: #ffffff !important;
            color: #334155 !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: var(--hra-radius-sm) !important;
            font-weight: 600 !important;
            transition: all 0.15s ease !important;
        }

        [data-testid="stMain"] button[kind="secondary"]:hover,
        [data-testid="stButton"] button:hover {
            background: #f8fafc !important;
            border-color: #94a3b8 !important;
            color: #0f172a !important;
        }

        /* Expander Cards (Patient Records) */
        [data-testid="stExpander"] {
            background: var(--hra-card-bg) !important;
            border: 1px solid var(--hra-card-border) !important;
            border-radius: var(--hra-radius-md) !important;
            box-shadow: var(--hra-shadow-sm) !important;
            margin-bottom: 0.9rem !important;
            overflow: hidden !important;
            transition: border-color 0.15s ease;
        }

        [data-testid="stExpander"]:hover {
            border-color: var(--hra-card-hover-border) !important;
        }

        [data-testid="stExpander"] summary {
            padding: 0.85rem 1.25rem !important;
            font-weight: 600 !important;
            color: var(--hra-text-main) !important;
        }

        /* Biomarker Vitals Pill */
        .vital-badge {
            display: inline-flex;
            flex-direction: column;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: var(--hra-radius-sm);
            padding: 0.5rem 0.85rem;
            min-width: 130px;
        }

        .vital-badge-label {
            font-size: 0.72rem;
            color: #64748b;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.04em;
        }

        .vital-badge-value {
            font-size: 1.1rem;
            font-weight: 700;
            color: #0f172a;
            margin-top: 2px;
            font-family: 'JetBrains Mono', monospace;
        }

        .vital-badge-unit {
            font-size: 0.72rem;
            font-weight: 400;
            color: #94a3b8;
            margin-left: 2px;
        }

        /* Clinical AI Insight Box */
        .ai-triage-card {
            background: #f0fdfa;
            border: 1px solid #99f6e4;
            border-radius: var(--hra-radius-md);
            padding: 1.25rem 1.4rem;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }

        .ai-triage-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.75rem;
        }

        .ai-triage-title {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 700;
            color: #0f766e;
            font-size: 0.95rem;
        }

        .ai-offline-card {
            background: #fffbeb;
            border: 1px solid #fde68a;
            border-radius: var(--hra-radius-md);
            padding: 1.15rem 1.35rem;
            margin: 1rem 0;
        }

        .ai-offline-header {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 700;
            color: #92400e;
            font-size: 0.95rem;
            margin-bottom: 0.4rem;
        }

        .ai-offline-text {
            color: #78350f;
            font-size: 0.88rem;
            line-height: 1.45;
            margin: 0;
        }

        /* Disclaimer Notice */
        .clinical-disclaimer {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: var(--hra-radius-md);
            padding: 0.9rem 1.2rem;
            margin-bottom: 1.5rem;
            font-size: 0.85rem;
            color: #1e40af;
            line-height: 1.45;
        }

        /* Sidebar Brand Header */
        .sidebar-brand {
            padding: 0.5rem 0.25rem 1.25rem 0.25rem;
            border-bottom: 1px solid var(--hra-navy-border);
            margin-bottom: 1.25rem;
        }

        .sidebar-brand-title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.22rem;
            font-weight: 800;
            color: #ffffff !important;
            letter-spacing: -0.02em;
            margin: 0;
        }

        .sidebar-brand-sub {
            font-size: 0.75rem;
            color: #94a3b8 !important;
            margin: 4px 0 0 32px;
            font-weight: 500;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        /* Sidebar System Status Pill */
        .sidebar-footer {
            margin-top: 2rem;
            padding: 1rem 0.5rem 0.5rem 0.5rem;
            border-top: 1px solid var(--hra-navy-border);
        }

        .sidebar-status-pill {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: var(--hra-radius-sm);
            padding: 0.45rem 0.75rem;
            font-size: 0.75rem;
            margin-bottom: 0.4rem;
        }

        /* Clean SaaS Light Data Table */
        .saas-table, table.saas-table {
            width: 100% !important;
            border-collapse: separate !important;
            border-spacing: 0 !important;
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            margin-bottom: 1.5rem !important;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05) !important;
            font-size: 0.9rem !important;
            color: #0f172a !important;
        }

        .saas-table th, table.saas-table th {
            background-color: #f8fafc !important;
            color: #475569 !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            font-size: 0.75rem !important;
            letter-spacing: 0.04em !important;
            padding: 0.85rem 1rem !important;
            border-bottom: 1px solid #e2e8f0 !important;
            text-align: left !important;
        }

        .saas-table td, table.saas-table td {
            padding: 0.85rem 1rem !important;
            border-bottom: 1px solid #f1f5f9 !important;
            color: #0f172a !important;
            background-color: #ffffff !important;
        }

        .saas-table tr:nth-child(even) td {
            background-color: #f8fafc !important;
        }

        .saas-table tr:hover td {
            background-color: #f1f5f9 !important;
        }

        /* Force pure white chart containers */
        [data-testid="stVegaLiteChart"], .vega-embed {
            background: #ffffff !important;
            border-radius: 12px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
