"""
app.py — Streamlit Starter: Entry Point & Authentication Gate
=============================================================
Application structure:
  1. Load Environment Variables from .env
  2. Check AUTH_MODE (mock or Azure AD)
  3. If not logged in → Show Login page and call st.stop()
  4. If logged in → Show Sidebar and standard Navigation

Design principles (based on streamlit/agent-skills):
  - Use st.navigation() for Multi-page routing (Streamlit >= 1.36)
  - Auth gate is handled in app.py at the top level, not scattered across pages
  - session_state.user stores user data globally
"""

import os
from dotenv import load_dotenv
import streamlit as st

# ── Load .env before everything else ─────────────────────────
load_dotenv()

# ── Page Config ───────────────────────────────────────────────
APP_TITLE = os.getenv("APP_TITLE", "My Dashboard")
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Select Auth Module ─────────────────────────────────────────
USE_MOCK = os.getenv("USE_MOCK_AUTH", "true").lower() == "true"

if USE_MOCK:
    from auth.mock_auth import mock_login_ui as login_ui, mock_logout as logout_fn
else:
    from auth.azure_ad import azure_login_ui as login_ui, azure_logout as logout_fn

# ── Auth Gate: Stop execution if not logged in ────────────────────────
if not st.session_state.get("authenticated"):
    login_ui()
    st.stop()

# ── This section runs only after a successful login ───────────────────────
user = st.session_state.get("user", {})

# ── CSS Injection: Dark Theme ─────────────────────────────────
st.markdown("""
<style>
    .stApp { background: radial-gradient(ellipse at top, #13132b, #0a0a1a); }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    /* Sidebar user card */
    .user-card {
        background: rgba(99,102,241,0.08);
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.75rem;
    }
    /* Metric value color */
    div[data-testid="stMetricValue"] {
        color: #a78bfa;
        font-size: 2rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"""<div class="user-card">
            <div style="font-weight:600; font-size:0.95rem;">👤 {user.get('name', 'User')}</div>
            <div style="color:#94a3b8; font-size:0.8rem;">{user.get('email', '')}</div>
            <div style="margin-top:4px;">
                <span style="background:#6366f1; color:white; padding:2px 8px;
                       border-radius:999px; font-size:0.7rem;">
                    {user.get('role', 'user').upper()}
                </span>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.divider()
    if st.button("🚪 Sign Out", use_container_width=True):
        logout_fn()

# ── Multi-page Navigation ─────────────────────────────────────
dashboard_page = st.Page(
    "pages/1_dashboard.py",
    title="Dashboard",
    icon="📊",
    default=True,
)
data_entry_page = st.Page(
    "pages/2_data_entry.py",
    title="Data Entry",
    icon="📝",
)

pg = st.navigation([dashboard_page, data_entry_page])
pg.run()
