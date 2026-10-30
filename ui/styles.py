import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #f5f8fa; }
        [data-testid="stSidebar"] { background: #0c2533; }
        [data-testid="stSidebar"] * { color: #e6f4f1 !important; }
        .hero { background: linear-gradient(135deg,#0c2533,#167d78); color:white;
                padding:2rem; border-radius:18px; margin-bottom:1.5rem; }
        .metric-card { background:white; border:1px solid #e4ecef; border-radius:14px;
                       padding:1.2rem; box-shadow:0 4px 18px rgba(12,37,51,.06); }
        </style>
        """,
        unsafe_allow_html=True,
    )
