# 🔧 Environment Variables for databricks_git_app.py

## Required Environment Variables

These environment variables must be set in your `app.yaml` or `.env` file for `databricks_git_app.py` to work correctly.

### ✅ Already Configured (from your current app.yaml)

```yaml
- name: DATABRICKS_SERVER_HOSTNAME
  value: "your-workspace.azuredatabricks.net"

- name: DATABRICKS_HTTP_PATH
  value: "sql/warehouses/your-warehouse-id"

- name: DATABRICKS_TOKEN
  value: "your-token-here"

- name: DATABRICKS_SCHEMA
  value: "users.kenzo_ohashi"
```

### 🆕 New Variables Needed for databricks_git_app.py

Add these to your `app.yaml` in the `env:` section:

#### ⚠️ IMPORTANT: Create Your Own AI Agent

**You MUST create your own Databricks AI agent** - you cannot reuse the example endpoint below!

**Steps:**
1. In Databricks: Go to **Machine Learning → Serving**
2. Click **"Create serving endpoint"**
3. Choose your model (GPT-4, Llama, etc.)
4. Name it (e.g., `fortnite-analytics-agent`)
5. Copy your endpoint name → use it below as `AI_AGENT_ENDPOINT`

```yaml
# AI Agent endpoint name (for the chatbot)
# ⚠️ REPLACE THIS with YOUR OWN endpoint name from Databricks ML Serving
- name: AI_AGENT_ENDPOINT
  value: "your-ai-agent-endpoint"  # ← Change this!

# Databricks dashboard ID (for embedded analytics)
# Get this from: Dashboards → Your Dashboard → Share → Embed
- name: DATABRICKS_DASHBOARD_ID
  value: "your-dashboard-id-here"  # ← Change this!

# Optional: Workspace ID (usually auto-extracted from hostname)
# - name: DATABRICKS_WORKSPACE_ID
#   value: "984752964297111"
```

## Complete app.yaml Example

Here's what your complete `app.yaml` should look like:

```yaml
command: [
  "python",
  "databricks_git_app.py"  # Or databricks_app.py if you renamed it
]

env:
  # Connection settings
  - name: DATABRICKS_SERVER_HOSTNAME
    value: "https://adb-XXXXXXXXX.XX.azuredatabricks.net/?o=XXXXXXXXX"
  
  - name: DATABRICKS_HTTP_PATH
    value: "sql/warehouses/XXXXXXXXXXXXXXXX"
  
  - name: DATABRICKS_TOKEN
    value: "dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  
  - name: DATABRICKS_SCHEMA
    value: "users.your_username"
  
  # AI Agent configuration (NEW)
  - name: AI_AGENT_ENDPOINT
    value: "your-ai-agent-endpoint"
  
  # Dashboard configuration (NEW)
  - name: DATABRICKS_DASHBOARD_ID
    value: "your-dashboard-id-here"

dependencies:
  - dash>=2.14.0
  - plotly>=5.18.0
  - pandas>=2.0.0
  - databricks-sql-connector>=3.0.0
  - requests>=2.28.0
```

## How These Variables Are Used

| Variable | Used For | Default if Missing |
|----------|----------|-------------------|
| `DATABRICKS_SERVER_HOSTNAME` | Database connection & AI endpoint base URL | `'your-workspace.azuredatabricks.net'` |
| `DATABRICKS_HTTP_PATH` | SQL warehouse connection | *(Required)* |
| `DATABRICKS_TOKEN` | Authentication | *(Required)* |
| `DATABRICKS_SCHEMA` | Data tables location | `'catalog.schema'` |
| `AI_AGENT_ENDPOINT` | Chatbot AI model | `'your-ai-agent-endpoint'` |
| `DATABRICKS_DASHBOARD_ID` | Embedded analytics dashboard | `'your-dashboard-id'` |
| `DATABRICKS_WORKSPACE_ID` | Dashboard embedding (optional) | Auto-extracted from hostname |

## Quick Test

To verify your environment variables are loaded correctly, look for this in your app logs:

```
🔧 Configuration loaded:
   • Server: adb-984752964297111.11.azuredatabricks.net...
   • Schema: users.kenzo_ohashi
   • AI Endpoint: mas-aafd6535-endpoint
   • Dashboard ID: 01f0ba94e7c913139b4e56...
```

If you see `'your-ai-agent-endpoint'` or `'your-dashboard-id'`, those variables aren't set correctly!

