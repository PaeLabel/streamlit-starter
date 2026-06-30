from __future__ import annotations
"""
pages/1_dashboard.py — CSV Data Dashboard
==========================================
Dashboard page to display data from CSV retrieved from:
  - Azure Blob Storage  (Configure in .env: AZURE_STORAGE_*)
  - SharePoint          (Configure in .env: SHAREPOINT_*)

Page Structure:
  1. Select Data Source (Blob / SharePoint / Upload local file)
  2. Select the CSV file to display
  3. Show Summary Metrics (Row count, Column count, etc.)
  4. Display data table + Filters
  5. Auto-generate charts for numeric columns

NOTE: Change DEMO_DATA_SOURCE to "blob" or "sharepoint" based on your actual environment
"""

import os
import pandas as pd
import streamlit as st

st.title("📊 Dashboard")
st.caption("Data from CSV — Azure Blob Storage or SharePoint")

# ────────────────────────────────────────────────────────────────────
# Section 1: Select Data Source and Load Data
# ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("📁 Data Source")
    source = st.radio(
        "Connect to",
        options=["Upload CSV (Local)", "Azure Blob Storage", "SharePoint"],
        index=0,  # Default to Upload CSV for demo/dev
    )

df = None
source_label = ""

if source == "Upload CSV (Local)":
    # ── Dev Mode: Upload CSV from Local ──────────────────────
    uploaded = st.file_uploader(
        "Upload a CSV file",
        type=["csv"],
        help="Upload your CSV file to preview the dashboard",
    )
    if uploaded:
        df = pd.read_csv(uploaded)
        source_label = f"📄 {uploaded.name}"

elif source == "Azure Blob Storage":
    # ── Azure Blob Storage ──────────────────────────────────────
    from connectors.azure_blob import read_csv_from_blob, list_blobs

    with st.sidebar:
        blobs = list_blobs()
        csv_blobs = [b for b in blobs if b.endswith(".csv")]
        if csv_blobs:
            selected_blob = st.selectbox("Select file", csv_blobs)
            if selected_blob:
                df = read_csv_from_blob(selected_blob)
                source_label = f"☁️ {selected_blob}"
        else:
            st.warning("No CSV files found in Blob container")

elif source == "SharePoint":
    # ── SharePoint ──────────────────────────────────────────────
    from connectors.sharepoint import read_csv_from_sharepoint

    with st.sidebar:
        # NOTE: Enter the Server-relative URL of the file in SharePoint
        sp_url = st.text_input(
            "SharePoint file URL",
            placeholder="/sites/MySite/Shared Documents/data.csv",
        )
        if st.button("Load from SharePoint") and sp_url:
            df = read_csv_from_sharepoint(sp_url)
            source_label = f"📂 {sp_url.rsplit('/', 1)[-1]}"

# ────────────────────────────────────────────────────────────────────
# Section 2: Display Data if DataFrame is Loaded
# ────────────────────────────────────────────────────────────────────
if df is not None and not df.empty:
    # ── Summary Metrics ────────────────────────────────────────────
    num_cols = df.select_dtypes(include="number").columns.tolist()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📋 Total Rows", f"{len(df):,}")
    col2.metric("📐 Columns", len(df.columns))
    col3.metric("🔢 Numeric Cols", len(num_cols))
    col4.metric("❓ Missing Values", int(df.isnull().sum().sum()))

    st.caption(f"Source: {source_label}")
    st.divider()

    # ── Filter & Preview ───────────────────────────────────────────
    with st.expander("🔍 Filter Data", expanded=False):
        filter_cols = st.multiselect(
            "Filter columns to display",
            options=df.columns.tolist(),
            default=df.columns.tolist()[:10],  # Show first 10 columns
        )
        search_term = st.text_input("Search in data", placeholder="Type to filter rows...")

    # Filter columns
    display_df = df[filter_cols] if filter_cols else df
    
    # Filter rows based on search term
    if search_term:
        mask = display_df.astype(str).apply(
            lambda col: col.str.contains(search_term, case=False, na=False)
        ).any(axis=1)
        display_df = display_df[mask]

    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.caption(f"Showing {len(display_df):,} of {len(df):,} rows")

    # ── Charts ─────────────────────────────────────────────────────
    if num_cols:
        st.divider()
        st.subheader("📈 Charts")

        chart_col, config_col = st.columns([3, 1])

        with config_col:
            chart_type = st.selectbox("Chart type", ["Bar", "Line", "Area"])
            x_axis = st.selectbox(
                "X-axis",
                options=df.columns.tolist(),
                index=0,
            )
            y_axis = st.multiselect(
                "Y-axis (numeric)",
                options=num_cols,
                default=[num_cols[0]] if num_cols else [],
            )

        with chart_col:
            if y_axis:
                chart_df = df.set_index(x_axis)[y_axis] if x_axis != y_axis[0] else df[y_axis]
                if chart_type == "Bar":
                    st.bar_chart(chart_df)
                elif chart_type == "Line":
                    st.line_chart(chart_df)
                else:
                    st.area_chart(chart_df)
            else:
                st.info("Select at least one Y-axis column to display a chart")

    # ── Download Button ────────────────────────────────────────────
    st.divider()
    csv_export = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=csv_export,
        file_name="export.csv",
        mime="text/csv",
    )

else:
    # ── Empty State ────────────────────────────────────────────────
    st.info(
        "👈 Select a **Data Source** from the left sidebar and load a CSV file "
        "to view the dashboard.",
        icon="ℹ️",
    )
    st.markdown("""
    **Supported data sources:**
    - 📄 **Local CSV** — Upload a file directly (for testing)
    - ☁️ **Azure Blob Storage** — Configure `AZURE_STORAGE_*` in `.env`
    - 📂 **SharePoint** — Configure `SHAREPOINT_SITE_URL` in `.env`
    """)
