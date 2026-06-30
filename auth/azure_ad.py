"""
auth/azure_ad.py — Azure Active Directory Authentication (MSAL / OAuth2)
=========================================================================
"""
auth/azure_ad.py — Azure Active Directory Authentication (MSAL / OAuth2)
=========================================================================
Supports 2 modes:
  1. Authorization Code Flow  — For Web Apps where Users Login via browser
  2. Client Credentials Flow  — For Service-to-Service (backend automation)

Prerequisites:
  1. Register App in Azure Portal → App registrations
  2. Add Redirect URI: http://localhost:8501 (dev) or actual URL for production
  3. Set Client Secret in Certificates & secrets
  4. Grant API permissions: User.Read, openid, profile, email

OAuth2 Authorization Code Flow Process:
  1. User clicks "Sign in with Microsoft"
  2. Streamlit redirects to Microsoft Login Page (Azure AD)
  3. User enters credentials and consents
  4. Azure AD redirects back with ?code=... in URL
  5. We exchange that code for an Access Token + User Info
  6. Save user info into st.session_state

Required Environment variables:
  - AZURE_TENANT_ID
  - AZURE_CLIENT_ID
  - AZURE_CLIENT_SECRET
  - AZURE_REDIRECT_URI
  - AZURE_SCOPE (e.g. "User.Read openid profile email")
"""

import os
import streamlit as st

# ── Lazy import to prevent Errors if msal is not installed ──
try:
    import msal
    MSAL_AVAILABLE = True
except ImportError:
    MSAL_AVAILABLE = False


def _get_msal_app() -> "msal.ConfidentialClientApplication":
    """Create and return MSAL Client Application (cached in session state)"""
    if not MSAL_AVAILABLE:
        st.error("Please install msal: `pip install msal`")
        st.stop()

    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    if not all([tenant_id, client_id, client_secret]):
        st.error(
            "Please configure AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET in .env"
        )
        st.stop()

    authority = f"https://login.microsoftonline.com/{tenant_id}"
    return msal.ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=authority,
    )


def get_auth_url() -> str:
    """Generate URL to redirect users to Microsoft Login Page"""
    app = _get_msal_app()
    scope = os.getenv("AZURE_SCOPE", "User.Read openid profile email").split()
    redirect_uri = os.getenv("AZURE_REDIRECT_URI", "http://localhost:8501")

    auth_url = app.get_authorization_request_url(
        scopes=scope,
        redirect_uri=redirect_uri,
        state="streamlit_oauth_state",
    )
    return auth_url


from typing import Optional

def exchange_code_for_token(auth_code: str) -> Optional[dict]:
    """
    Exchange authorization code from callback URL for an Access Token

    Returns:
        dict with access_token, id_token, and claims
        or None if failed
    """
    app = _get_msal_app()
    scope = os.getenv("AZURE_SCOPE", "User.Read openid profile email").split()
    redirect_uri = os.getenv("AZURE_REDIRECT_URI", "http://localhost:8501")

    result = app.acquire_token_by_authorization_code(
        code=auth_code,
        scopes=scope,
        redirect_uri=redirect_uri,
    )

    if "error" in result:
        st.error(f"Authentication error: {result.get('error_description')}")
        return None

    return result


def get_user_info(token_result: dict) -> dict:
    """
    Extract User data from ID Token claims

    Returns:
        dict containing username, name, email, role
    """
    claims = token_result.get("id_token_claims", {})
    return {
        "username": claims.get("preferred_username", claims.get("upn", "unknown")),
        "name": claims.get("name", "Unknown User"),
        "email": claims.get("email", claims.get("preferred_username", "")),
        "role": "user",  # ← Adjust to fetch Role from Azure AD Groups
        "oid": claims.get("oid", ""),  # Object ID in Azure AD
    }


def azure_login_ui() -> bool:
    """
    Display Login page for Azure AD OAuth2

    Mechanism:
      - Check query params to see if ?code= was sent from Azure
      - If yes: exchange code → token → user info → save to session state
      - If no: show "Sign in with Microsoft" button

    Returns:
        True if authenticated
    """
    query_params = st.query_params

    # ── Step 2: Azure redirects back with ?code= ───────────────
    if "code" in query_params and not st.session_state.get("authenticated"):
        auth_code = query_params["code"]
        with st.spinner("Completing sign in..."):
            token_result = exchange_code_for_token(auth_code)
            if token_result:
                user_info = get_user_info(token_result)
                st.session_state.authenticated = True
                st.session_state.user = user_info
                st.session_state.access_token = token_result.get("access_token")
                # Clear query params from URL after successful login
                st.query_params.clear()
                st.rerun()

    # ── Step 1: Show Login UI ────────────────────────────────────
    if not st.session_state.get("authenticated"):
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown(
                "<h2 style='text-align:center;'>🔐 Sign In</h2>",
                unsafe_allow_html=True,
            )
            st.divider()
            auth_url = get_auth_url()
            st.link_button(
                "🏢 Sign in with Microsoft",
                url=auth_url,
                use_container_width=True,
                type="primary",
            )
        return False

    return True


def azure_logout():
    """Clear session state and redirect to Azure logout endpoint"""
    tenant_id = os.getenv("AZURE_TENANT_ID", "common")
    logout_url = (
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/logout"
        f"?post_logout_redirect_uri={os.getenv('AZURE_REDIRECT_URI', 'http://localhost:8501')}"
    )
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # Redirect to Azure logout endpoint
    st.markdown(f'<meta http-equiv="refresh" content="0;url={logout_url}">', unsafe_allow_html=True)
    st.stop()
