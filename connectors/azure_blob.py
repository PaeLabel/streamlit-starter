"""
connectors/azure_blob.py — Azure Blob Storage CSV Connector
============================================================
Read and write CSV files from/to Azure Blob Storage

Mechanism:
  - Uses azure-storage-blob SDK
  - @st.cache_data prevents re-fetching data on every rerun
  - Supports both Connection String and Account Key + Account Name

Required Environment variables:
  - AZURE_STORAGE_ACCOUNT_NAME
  - AZURE_STORAGE_ACCOUNT_KEY   (or AZURE_STORAGE_CONNECTION_STRING)
  - AZURE_BLOB_CONTAINER_NAME

Example Usage:
    from connectors.azure_blob import read_csv_from_blob, write_csv_to_blob
    df = read_csv_from_blob("reports/sales_2024.csv")
    write_csv_to_blob(df, "reports/sales_2024_updated.csv")
"""

import io
import os
import pandas as pd
import streamlit as st

try:
    from azure.storage.blob import BlobServiceClient, BlobClient
    AZURE_BLOB_AVAILABLE = True
except ImportError:
    AZURE_BLOB_AVAILABLE = False


def _get_blob_service_client() -> "BlobServiceClient":
    """Create and return BlobServiceClient"""
    if not AZURE_BLOB_AVAILABLE:
        st.error("Please install: `pip install azure-storage-blob`")
        st.stop()

    # ── Method 1: Use Connection String ──────────────────────────
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if conn_str:
        return BlobServiceClient.from_connection_string(conn_str)

    # ── Method 2: Use Account Name + Account Key ─────────────────
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
    if account_name and account_key:
        url = f"https://{account_name}.blob.core.windows.net"
        return BlobServiceClient(account_url=url, credential=account_key)

    st.error(
        "Please configure AZURE_STORAGE_CONNECTION_STRING or "
        "AZURE_STORAGE_ACCOUNT_NAME + AZURE_STORAGE_ACCOUNT_KEY in .env"
    )
    st.stop()


@st.cache_data(ttl=300, show_spinner="Loading data from Blob Storage...")
def read_csv_from_blob(blob_path: str, **kwargs) -> pd.DataFrame:
    """
    Read CSV file from Azure Blob Storage and return as DataFrame

    Args:
        blob_path: path inside container e.g. "reports/sales.csv"
        **kwargs: passed directly to pd.read_csv() e.g. dtype={}, parse_dates=[]

    Returns:
        pd.DataFrame

    Example:
        df = read_csv_from_blob("data/customers.csv", parse_dates=["created_at"])
    """
    container = os.getenv("AZURE_BLOB_CONTAINER_NAME")
    if not container:
        st.error("Please configure AZURE_BLOB_CONTAINER_NAME in .env")
        st.stop()

    client = _get_blob_service_client()
    blob_client: BlobClient = client.get_blob_client(
        container=container, blob=blob_path
    )

    # Download blob and convert to DataFrame
    stream = blob_client.download_blob()
    content = stream.readall()
    return pd.read_csv(io.BytesIO(content), **kwargs)


def write_csv_to_blob(df: pd.DataFrame, blob_path: str, overwrite: bool = True) -> bool:
    """
    Write DataFrame as a CSV file to Azure Blob Storage

    Args:
        df: DataFrame to save
        blob_path: destination path e.g. "reports/sales_updated.csv"
        overwrite: allow overwriting existing file (default: True)

    Returns:
        True if successful

    Example:
        success = write_csv_to_blob(df, "data/customers.csv")
    """
    container = os.getenv("AZURE_BLOB_CONTAINER_NAME")
    client = _get_blob_service_client()
    blob_client: BlobClient = client.get_blob_client(
        container=container, blob=blob_path
    )

    # Convert DataFrame to CSV bytes
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    blob_client.upload_blob(csv_bytes, overwrite=overwrite)

    # Clear cache so next read fetches new data
    read_csv_from_blob.clear()
    return True


def list_blobs(prefix: str = "") -> list[str]:
    """
    List all blobs in the container (filterable by prefix)

    Args:
        prefix: filter only blobs starting with this prefix

    Returns:
        list of blob names

    Example:
        files = list_blobs("reports/2024/")
    """
    container = os.getenv("AZURE_BLOB_CONTAINER_NAME")
    client = _get_blob_service_client()
    container_client = client.get_container_client(container)
    return [blob.name for blob in container_client.list_blobs(name_starts_with=prefix)]
