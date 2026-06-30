"""
connectors/sharepoint.py — SharePoint CSV Connector via Microsoft Graph API
===========================================================================
Read and write CSV files from/to a SharePoint Document Library

Mechanism:
  - Uses Office365-REST-Python-Client (or Microsoft Graph REST API)
  - Authentication via Azure AD Client Credentials (App-only)
    or using User's Access Token (Delegated)
  - @st.cache_data prevents re-fetching data on every rerun

2 Execution modes:
  1. App-only (Client Credentials): Uses AZURE_CLIENT_ID + AZURE_CLIENT_SECRET
     — Suitable for Background Jobs, No user login required
     — Requires Admin consent for Sites.ReadWrite.All
  2. On-behalf-of (Delegated): Uses Access Token of logged-in User
     — Suitable for Web Apps where Users login via Azure AD
     — Uses logged-in User's permissions (No Admin consent required)

Required Environment variables:
  - AZURE_TENANT_ID
  - AZURE_CLIENT_ID
  - AZURE_CLIENT_SECRET
  - SHAREPOINT_SITE_URL  (e.g. https://company.sharepoint.com/sites/MySite)

Example Usage:
    from connectors.sharepoint import read_csv_from_sharepoint, write_csv_to_sharepoint
    df = read_csv_from_sharepoint("/Shared Documents/Data/sales.csv")
    write_csv_to_sharepoint(df, "/Shared Documents/Data/sales.csv")
"""

import io
import os
import pandas as pd
import streamlit as st

try:
    from office365.runtime.auth.client_credential import ClientCredential
    from office365.sharepoint.client_context import ClientContext
    SP_AVAILABLE = True
except ImportError:
    SP_AVAILABLE = False


def _get_sp_context() -> "ClientContext":
    """
    Create and return SharePoint ClientContext
    Uses App-only credentials (Client ID + Secret)
    """
    if not SP_AVAILABLE:
        st.error(
            "Please install: `pip install Office365-REST-Python-Client`"
        )
        st.stop()

    site_url = os.getenv("SHAREPOINT_SITE_URL")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    if not all([site_url, client_id, client_secret]):
        st.error(
            "Please configure SHAREPOINT_SITE_URL, AZURE_CLIENT_ID, "
            "AZURE_CLIENT_SECRET in .env"
        )
        st.stop()

    credentials = ClientCredential(client_id, client_secret)
    return ClientContext(site_url).with_credentials(credentials)


@st.cache_data(ttl=300, show_spinner="Loading data from SharePoint...")
def read_csv_from_sharepoint(file_relative_url: str, **kwargs) -> pd.DataFrame:
    """
    Read CSV file from SharePoint and return as DataFrame

    Args:
        file_relative_url: Server-relative URL of the file
                           e.g. "/sites/MySite/Shared Documents/data.csv"
        **kwargs: passed directly to pd.read_csv()

    Returns:
        pd.DataFrame

    Example:
        df = read_csv_from_sharepoint(
            "/sites/Data/Shared Documents/reports/sales.csv",
            parse_dates=["date"]
        )
    """
    ctx = _get_sp_context()

    # Download file from SharePoint
    file = ctx.web.get_file_by_server_relative_url(file_relative_url)
    response = file.download()
    ctx.execute_query()

    # Convert bytes to DataFrame
    content = response.content
    return pd.read_csv(io.BytesIO(content), **kwargs)


def write_csv_to_sharepoint(
    df: pd.DataFrame,
    file_relative_url: str,
) -> bool:
    """
    Write DataFrame as a CSV file to SharePoint

    Args:
        df: DataFrame to save
        file_relative_url: Destination Server-relative URL
                           e.g. "/sites/MySite/Shared Documents/data.csv"

    Returns:
        True if successful

    Example:
        write_csv_to_sharepoint(df, "/sites/MySite/Shared Documents/data.csv")
    """
    ctx = _get_sp_context()

    # Convert DataFrame to CSV bytes
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    csv_stream = io.BytesIO(csv_bytes)

    # Separate folder path and filename
    parts = file_relative_url.rsplit("/", 1)
    folder_url = parts[0]
    filename = parts[1]

    # Upload to SharePoint folder
    folder = ctx.web.get_folder_by_server_relative_url(folder_url)
    folder.upload_file(filename, csv_stream)
    ctx.execute_query()

    # Clear cache
    read_csv_from_sharepoint.clear()
    return True
