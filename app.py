"""
app.py — Streamlit Starter: Entry Point & Authentication Gate
=============================================================
โครงสร้างหลักของแอปพลิเคชัน:
  1. โหลด Environment Variables จาก .env
  2. ตรวจสอบ AUTH_MODE (mock หรือ Azure AD)
  3. ถ้ายังไม่ได้ Login → แสดงหน้า Login แล้ว st.stop()
  4. ถ้า Login แล้ว → แสดง Sidebar และ Navigation ปกติ

หลักการออกแบบ (ตาม streamlit/agent-skills):
  - ใช้ st.navigation() สำหรับ Multi-page routing (Streamlit >= 1.36)
  - Auth gate อยู่ที่ app.py ชั้นเดียว ไม่กระจายไปทุก page
  - session_state.user เก็บข้อมูล user ทั่วทั้งแอป
"""

import os
from dotenv import load_dotenv
import streamlit as st

# ── โหลด .env ก่อนสิ่งอื่นใดทั้งหมด ─────────────────────────
load_dotenv()

# ── Page Config ───────────────────────────────────────────────
APP_TITLE = os.getenv("APP_TITLE", "My Dashboard")
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── เลือก Auth Module ─────────────────────────────────────────
USE_MOCK = os.getenv("USE_MOCK_AUTH", "true").lower() == "true"

if USE_MOCK:
    from auth.mock_auth import mock_login_ui as login_ui, mock_logout as logout_fn
else:
    from auth.azure_ad import azure_login_ui as login_ui, azure_logout as logout_fn

# ── Auth Gate: หยุดถ้ายังไม่ได้ Login ────────────────────────
if not st.session_state.get("authenticated"):
    login_ui()
    st.stop()

# ── ส่วนนี้รันเมื่อ Login แล้วเท่านั้น ───────────────────────
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
