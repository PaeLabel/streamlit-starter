# Streamlit Starter Template

A production-ready Streamlit starter with Azure AD authentication, CSV data connectors for Azure Blob Storage and SharePoint, dashboard, and Excel-style data entry.

## 🏗️ Project Structure

```
StreamLit-Starter/
├── .env.example           # Environment variable template
├── .gitignore             # Git ignore (sensitive files excluded)
├── app.py                 # Entry point + Auth gate
├── requirements.txt       # Python dependencies
│
├── auth/
│   ├── azure_ad.py        # Azure AD OAuth2 (MSAL)
│   └── mock_auth.py       # Mock auth for local dev
│
├── connectors/
│   ├── azure_blob.py      # Azure Blob Storage CSV connector
│   └── sharepoint.py      # SharePoint CSV connector (Graph API)
│
├── pages/
│   ├── 1_dashboard.py     # Data dashboard with filters & charts
│   └── 2_data_entry.py    # Excel-style data entry (Create/Update)
│
└── .streamlit/
    └── config.toml        # Dark theme configuration
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
cd StreamLit-Starter

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your values
```

### 2. Run in Dev Mode (Mock Auth)

```bash
# .env: USE_MOCK_AUTH=true (default)
streamlit run app.py

# Login: admin / admin  or  viewer / viewer
```

### 3. Run with Azure AD Auth

```bash
# 1. Fill in .env:
#    AZURE_TENANT_ID=...
#    AZURE_CLIENT_ID=...
#    AZURE_CLIENT_SECRET=...
#    AZURE_REDIRECT_URI=http://localhost:8501
#    USE_MOCK_AUTH=false

streamlit run app.py
```

## 🔐 Authentication

| Mode | Use Case | Config |
|---|---|---|
| **Mock** (default) | Local development | `USE_MOCK_AUTH=true` |
| **Azure AD** | Production | `USE_MOCK_AUTH=false` + Azure credentials |

## 📦 Data Connectors

### Azure Blob Storage
```python
from connectors.azure_blob import read_csv_from_blob, write_csv_to_blob
df = read_csv_from_blob("data/sales.csv")
write_csv_to_blob(df, "data/sales.csv")
```

### SharePoint
```python
from connectors.sharepoint import read_csv_from_sharepoint, write_csv_to_sharepoint
df = read_csv_from_sharepoint("/sites/MySite/Shared Documents/data.csv")
write_csv_to_sharepoint(df, "/sites/MySite/Shared Documents/data.csv")
```

## 📝 Adding Custom Columns to Data Entry

Edit `COLUMN_CONFIG` in `pages/2_data_entry.py`:

```python
COLUMN_CONFIG = {
    "name": st.column_config.TextColumn("Name", required=True),
    "amount": st.column_config.NumberColumn("Amount", format="฿%,.2f"),
    "status": st.column_config.SelectboxColumn("Status", options=["active", "inactive"]),
    "date": st.column_config.DateColumn("Date"),
}
```

## ⚙️ Environment Variables Reference

See [`.env.example`](.env.example) for all available variables.
