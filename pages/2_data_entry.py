"""
pages/2_data_entry.py — Excel-style Data Entry (Create / Update)
=================================================================
"""
pages/2_data_entry.py — Excel-style Data Entry (Create / Update)
=================================================================
Page for entering and editing data like Excel via st.data_editor

Features:
  1. Load data from CSV (Blob / SharePoint / Local)
  2. Edit data in an Excel-like Grid (inline editing)
  3. Add new rows directly from the Grid (st.data_editor allows + row)
  4. Delete selected rows
  5. Click save to push data back to Blob / SharePoint

Execution Model:
  - Original data (original_df) is stored in session_state
  - Edited data (edited_df) comes from st.data_editor
  - When Save is clicked, it writes back to the source

Supported Column Types in st.data_editor:
  - TextColumn, NumberColumn, DateColumn, CheckboxColumn, SelectboxColumn
  Adjustable in COLUMN_CONFIG below
"""

import os
import pandas as pd
import streamlit as st

st.title("📝 Data Entry")
st.caption("Create and update records — Excel-style editing")

# ────────────────────────────────────────────────────────────────────
# ── Configure Column Config for st.data_editor ─────────────────────
# Edit this section to match your data structure
# ────────────────────────────────────────────────────────────────────
# Example Column Config — adjust to match your CSV
COLUMN_CONFIG = {
    # "id": st.column_config.NumberColumn("ID", disabled=True),
    # "name": st.column_config.TextColumn("Name", required=True),
    # "amount": st.column_config.NumberColumn("Amount (฿)", min_value=0, format="฿%,.2f"),
    # "date": st.column_config.DateColumn("Date"),
    # "status": st.column_config.SelectboxColumn("Status", options=["active","inactive","pending"]),
    # "approved": st.column_config.CheckboxColumn("Approved"),
}

# ── Sample schema for demo when no data is loaded ─────────────────
SAMPLE_SCHEMA = {
    "id": pd.Series(dtype="int64"),
    "name": pd.Series(dtype="str"),
    "email": pd.Series(dtype="str"),
    "department": pd.Series(dtype="str"),
    "amount": pd.Series(dtype="float64"),
    "date": pd.Series(dtype="object"),
    "status": pd.Series(dtype="str"),
}

# ────────────────────────────────────────────────────────────────────
# Section 1: Select Data Source and Load Data
# ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("📁 Data Source")
    source = st.radio(
        "Connect to",
        options=["Sample Data (Demo)", "Upload CSV", "Azure Blob Storage", "SharePoint"],
        index=0,
    )

# ── Initialize session state to store DataFrame ─────────────────
if "entry_df" not in st.session_state:
    st.session_state.entry_df = None
if "entry_source_path" not in st.session_state:
    st.session_state.entry_source_path = None
if "entry_source_type" not in st.session_state:
    st.session_state.entry_source_type = None

# ── Load data based on Source ──────────────────────────────────────────
if source == "Sample Data (Demo)":
    if st.session_state.entry_df is None:
        st.session_state.entry_df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Somchai Jaidee", "Nattapon Klinkaew", "Pranee Suwannee"],
            "email": ["somchai@example.com", "nattapon@biz.th", "pranee@mail.com"],
            "department": ["Sales", "IT", "HR"],
            "amount": [45000.0, 62000.0, 38000.0],
            "date": ["2024-01-15", "2024-02-20", "2024-03-10"],
            "status": ["active", "active", "inactive"],
        })
        st.session_state.entry_source_type = "demo"

elif source == "Upload CSV":
    uploaded = st.file_uploader("Upload CSV to edit", type=["csv"])
    if uploaded:
        st.session_state.entry_df = pd.read_csv(uploaded)
        st.session_state.entry_source_type = "upload"
        st.session_state.entry_source_path = uploaded.name

elif source == "Azure Blob Storage":
    from connectors.azure_blob import read_csv_from_blob, write_csv_to_blob, list_blobs
    with st.sidebar:
        blobs = list_blobs()
        csv_blobs = [b for b in blobs if b.endswith(".csv")]
        selected_blob = st.selectbox("Select file to edit", csv_blobs) if csv_blobs else None
        if st.button("Load") and selected_blob:
            st.session_state.entry_df = read_csv_from_blob(selected_blob)
            st.session_state.entry_source_type = "blob"
            st.session_state.entry_source_path = selected_blob

elif source == "SharePoint":
    from connectors.sharepoint import read_csv_from_sharepoint, write_csv_to_sharepoint
    with st.sidebar:
        sp_url = st.text_input("SharePoint file URL", placeholder="/sites/.../data.csv")
        if st.button("Load") and sp_url:
            st.session_state.entry_df = read_csv_from_sharepoint(sp_url)
            st.session_state.entry_source_type = "sharepoint"
            st.session_state.entry_source_path = sp_url

# ────────────────────────────────────────────────────────────────────
# Section 2: Excel-style Data Editor
# ────────────────────────────────────────────────────────────────────
if st.session_state.entry_df is not None:
    df = st.session_state.entry_df

    # ── Toolbar ────────────────────────────────────────────────────
    tool_col1, tool_col2, tool_col3, tool_col4 = st.columns([2, 1, 1, 1])
    with tool_col1:
        st.caption(
            f"📋 **{len(df):,} rows** × **{len(df.columns)} columns** "
            f"| Source: `{st.session_state.entry_source_path or 'Demo'}`"
        )

    # ── st.data_editor: Excel-style Editable Grid ──────────────────
    # Features included:
    #   - Click a cell to type and edit immediately
    #   - Click + at the bottom to add a new row
    #   - Select the left checkbox and click delete to remove a row
    edited_df: pd.DataFrame = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",          # ← Allow adding/deleting rows
        hide_index=False,            # Show index for reference
        column_config=COLUMN_CONFIG or None,
        key="data_editor_main",
    )

    st.caption(
        "💡 **Tips:** Click a cell to edit | "
        "Click ➕ below the table to add a row | "
        "Select ☑️ and click 🗑 to delete a row"
    )
    st.divider()

    # ── Action Buttons ─────────────────────────────────────────────
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])

    with btn_col1:
        # ── Save back to Source ────────────────────────────────────
        if st.button("💾 Save Changes", type="primary", use_container_width=True):
            source_type = st.session_state.entry_source_type
            source_path = st.session_state.entry_source_path

            if source_type == "demo" or source_type == "upload":
                # For demo or upload, just update session state
                st.session_state.entry_df = edited_df
                st.success("✅ Changes saved to session (not persisted for demo/upload)")

            elif source_type == "blob":
                with st.spinner("Saving to Azure Blob Storage..."):
                    write_csv_to_blob(edited_df, source_path)
                st.session_state.entry_df = edited_df
                st.success(f"✅ Saved to Azure Blob: `{source_path}`")

            elif source_type == "sharepoint":
                with st.spinner("Saving to SharePoint..."):
                    write_csv_to_sharepoint(edited_df, source_path)
                st.session_state.entry_df = edited_df
                st.success(f"✅ Saved to SharePoint: `{source_path}`")

    with btn_col2:
        # ── Reset ────────────────────────────────────────────────
        if st.button("↩️ Reset Changes", use_container_width=True):
            st.rerun()

    with btn_col3:
        # ── Download ─────────────────────────────────────────────
        csv_bytes = edited_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download as CSV",
            data=csv_bytes,
            file_name="edited_data.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # ── Change Summary ─────────────────────────────────────────────
    with st.expander("🔍 View Changes Summary", expanded=False):
        original = st.session_state.entry_df
        rows_added = max(0, len(edited_df) - len(original))
        rows_removed = max(0, len(original) - len(edited_df))
        
        sum_col1, sum_col2 = st.columns(2)
        sum_col1.metric("Rows Added", rows_added, delta=rows_added or None)
        sum_col2.metric("Rows Removed", rows_removed, delta=-rows_removed or None)
        
        st.markdown("**Edited DataFrame Preview:**")
        st.dataframe(edited_df, use_container_width=True, hide_index=True)

else:
    # ── Empty State ────────────────────────────────────────────────
    st.info(
        "👈 Select a **Data Source** from the left sidebar to start editing data.",
        icon="📝",
    )
    st.markdown("""
    **How to use Data Entry:**
    - 🎯 **Sample Data** — Start experimenting immediately without real data connections
    - 📄 **Upload CSV** — Upload a CSV file from your machine
    - ☁️ **Azure Blob Storage** — Connect to your Blob Storage
    - 📂 **SharePoint** — Connect and edit files on SharePoint

    **Features:**
    - ✏️ Edit data in an Excel-like Grid (click cell and type)
    - ➕ Add a new row using the button below the table
    - 🗑️ Delete rows by selecting checkboxes and clicking the delete button
    - 💾 Save directly back to the Source (Blob / SharePoint)
    - ⬇️ Download data as CSV
    """)
