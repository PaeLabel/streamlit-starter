"""
auth/mock_auth.py — Mock Authentication for Local Development
=============================================================
Used for local testing without real Azure AD
Controlled by USE_MOCK_AUTH=true in .env

Usage (in app.py):
    from auth.mock_auth import mock_login_ui, mock_logout

Mechanism:
    - Check st.session_state.authenticated
    - If not logged in, show simple username/password form
    - Accepted users are defined in MOCK_USERS dict below
"""

import streamlit as st

# ── Mock Users for Dev/Test ──────────────────────────────
# key: username, value: {"password": str, "name": str, "role": str}
MOCK_USERS: dict = {
    "admin": {"password": "admin", "name": "Admin User", "role": "admin"},
    "viewer": {"password": "viewer", "name": "View Only User", "role": "viewer"},
}


def mock_login_ui() -> bool:
    """
    Display Mock Login page and return True if successful

    Usage example:
        if not st.session_state.get("authenticated"):
            if not mock_login_ui():
                st.stop()
    """
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(
            "<h2 style='text-align:center;'>🔐 Sign In</h2>"
            "<p style='text-align:center; color:gray; font-size:0.85rem;'>"
            "[DEV MODE] Mock Authentication</p>",
            unsafe_allow_html=True,
        )
        st.divider()
        with st.form("mock_login_form"):
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="admin")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            user = MOCK_USERS.get(username)
            if user and user["password"] == password:
                st.session_state.authenticated = True
                st.session_state.user = {
                    "username": username,
                    "name": user["name"],
                    "role": user["role"],
                    "email": f"{username}@mock.local",
                }
                st.rerun()
            else:
                st.error("Invalid username or password")

        st.caption("Dev credentials — admin / admin or viewer / viewer")
    return st.session_state.get("authenticated", False)


def mock_logout():
    """Clear all session state and rerun"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
