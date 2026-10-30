import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --hra-page: #f4f8fa;
            --hra-surface: #ffffff;
            --hra-border: #d7e3e7;
            --hra-text: #17313d;
            --hra-muted: #54707b;
            --hra-accent: #087f7a;
            --hra-accent-dark: #05615e;
            --hra-shadow: rgba(12, 37, 51, .08);
        }
        .stApp, [data-testid="stAppViewContainer"] { background: var(--hra-page); }
        [data-testid="stSidebar"] { background: #0c2533; }
        [data-testid="stSidebar"] * { color: #e6f4f1 !important; }
        [data-testid="stSidebar"] label[data-testid="stRadioOption"] {
            border-radius: 10px;
            padding: .35rem .5rem;
        }
        [data-testid="stSidebar"] label[data-testid="stRadioOption"]:hover {
            background: rgba(255,255,255,.1);
        }
        [data-testid="stMain"] h1,
        [data-testid="stMain"] h2,
        [data-testid="stMain"] h3,
        [data-testid="stMain"] label,
        [data-testid="stMain"] p,
        [data-testid="stMain"] [data-testid="stMarkdownContainer"] {
            color: var(--hra-text);
        }
        [data-testid="stMain"] label {
            font-weight: 600;
            color: var(--hra-text) !important;
        }
        [data-testid="stMain"] input,
        [data-testid="stMain"] textarea,
        [data-testid="stMain"] [data-baseweb="select"] > div {
            background: var(--hra-surface) !important;
            color: var(--hra-text) !important;
            border: 1px solid var(--hra-border) !important;
            border-radius: 9px;
        }
        [data-testid="stMain"] input::placeholder,
        [data-testid="stMain"] textarea::placeholder {
            color: var(--hra-muted) !important;
            opacity: 1;
        }
        [data-testid="stMain"] input:focus,
        [data-testid="stMain"] textarea:focus {
            border-color: var(--hra-accent) !important;
            box-shadow: 0 0 0 2px rgba(8,127,122,.16) !important;
        }
        [data-testid="stMain"] [data-testid="stForm"] {
            background: var(--hra-surface);
            border: 1px solid var(--hra-border);
            border-radius: 16px;
            padding: 1.25rem 1.35rem .5rem;
            box-shadow: 0 5px 20px var(--hra-shadow);
        }
        [data-testid="stMain"] [data-testid="stFormSubmitButton"] button,
        [data-testid="stMain"] [data-testid="stButton"] button,
        [data-testid="stMain"] button[kind="primary"],
        [data-testid="stMain"] button[kind="secondary"] {
            color: #ffffff !important;
            background: var(--hra-accent) !important;
            border: 1px solid var(--hra-accent-dark) !important;
            border-radius: 9px;
            font-weight: 700;
        }
        [data-testid="stMain"] [data-testid="stFormSubmitButton"] button:hover,
        [data-testid="stMain"] [data-testid="stButton"] button:hover,
        [data-testid="stMain"] button[kind="primary"]:hover,
        [data-testid="stMain"] button[kind="secondary"]:hover {
            background: var(--hra-accent-dark) !important;
        }
        .hero {
            background: linear-gradient(135deg, #0c2533, #167d78);
            color: #ffffff;
            padding: 2rem;
            border-radius: 18px;
            margin-bottom: 1.5rem;
            box-shadow: 0 8px 24px rgba(12,37,51,.16);
        }
        .hero h1, .hero p { color: #ffffff !important; }
        .metric-card {
            background: var(--hra-surface);
            color: var(--hra-text);
            border: 1px solid var(--hra-border);
            border-radius: 14px;
            padding: 1.2rem;
            box-shadow: 0 4px 18px var(--hra-shadow);
        }
        .metric-card small { color: var(--hra-muted); }
        .metric-card h2 { color: var(--hra-text); margin: .25rem 0 0; }
        [data-testid="stExpander"] {
            background: var(--hra-surface);
            border: 1px solid var(--hra-border);
            border-radius: 12px;
        }
        @media (prefers-color-scheme: dark) {
            :root {
                --hra-page: #101b22;
                --hra-surface: #182832;
                --hra-border: #38505b;
                --hra-text: #e8f1f3;
                --hra-muted: #b7cbd0;
                --hra-shadow: rgba(0,0,0,.24);
            }
        }
        [data-theme="dark"] {
            --hra-page: #101b22;
            --hra-surface: #182832;
            --hra-border: #38505b;
            --hra-text: #e8f1f3;
            --hra-muted: #b7cbd0;
            --hra-shadow: rgba(0,0,0,.24);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
