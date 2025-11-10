# 🌍 Fortnite Creator Hub - Player Analytics Dashboard

<div align="center">

![Fortnite](https://img.shields.io/badge/Fortnite-Creator-9D4EDD?style=for-the-badge)
![Databricks](https://img.shields.io/badge/Databricks-Apps-FF006E?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-00D9FF?style=for-the-badge)
![Dash](https://img.shields.io/badge/Dash-2.14+-FF8800?style=for-the-badge)

**Interactive 3D globe visualization showing real-time player locations and analytics for Fortnite Creative islands.**

[Features](#-features) • [Quick Start](#-quick-start) • [Setup](#%EF%B8%8F-setup) • [Security](#-security) • [Documentation](#-documentation)

</div>

---

## ✨ Features

### 🌐 **Interactive 3D Globe**
- Auto-rotating orthographic projection with Fortnite-themed styling
- Real-time player location heatmap with color gradients
- Smooth animations and drag-to-explore functionality
- Updates every 5 minutes with live data

### 🤖 **AI-Powered Chatbot**
- Integrated Databricks AI agent for analytics insights
- Conversation memory for contextual responses
- Markdown-formatted responses with custom styling
- Dedicated "Key Insights" section with weekly summaries

### 📊 **Analytics Dashboard**
- Embedded Databricks AI/BI dashboards
- Real-time statistics (active sessions, locations, avg duration)
- Multi-page navigation with hamburger menu
- User authentication display

### 🎨 **Fortnite-Themed UI**
- Custom color scheme (Cyan, Pink, Orange)
- Glowing borders and shadows
- Responsive design for all screen sizes
- Dark mode optimized

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.9+
- Databricks workspace with SQL Warehouse
- Databricks AI agent (optional, for chatbot)

### **Installation**

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/fortnite-creator-hub.git
cd fortnite-creator-hub
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
# Copy the template
cp app.yaml.template app.yaml

# Edit with your Databricks credentials
nano app.yaml
```

4. **Deploy to Databricks Apps**
- Upload `databricks_git_app.py` and `app.yaml` to your Databricks workspace
- Deploy via Databricks Apps UI or CLI
- Access your app at the provided URL

---

## ⚙️ Setup

### **Required Environment Variables**

Create an `app.yaml` file with the following variables:

```yaml
env:
  - name: DATABRICKS_SERVER_HOSTNAME
    value: "your-workspace.azuredatabricks.net"
  
  - name: DATABRICKS_HTTP_PATH
    value: "sql/warehouses/your-warehouse-id"
  
  - name: DATABRICKS_TOKEN
    value: "your-databricks-token"
  
  - name: DATABRICKS_SCHEMA
    value: "your_catalog.your_schema"
  
  # Optional: For AI chatbot
  - name: AI_AGENT_ENDPOINT
    value: "your-ai-agent-endpoint"
  
  # Optional: For embedded dashboard
  - name: DATABRICKS_DASHBOARD_ID
    value: "your-dashboard-id"
```

### **Where to Find These Values**

| Variable | Location |
|----------|----------|
| `DATABRICKS_SERVER_HOSTNAME` | Browser URL when logged into Databricks |
| `DATABRICKS_HTTP_PATH` | SQL Warehouses → Your Warehouse → Connection Details |
| `DATABRICKS_TOKEN` | User Settings → Developer → Access Tokens |
| `DATABRICKS_SCHEMA` | Data Explorer in Databricks |
| `AI_AGENT_ENDPOINT` | Machine Learning → Serving → Your Endpoint (see below) |
| `DATABRICKS_DASHBOARD_ID` | Dashboards → Share → Embed |

---

## 🤖 Creating Your AI Agent

The chatbot feature requires a Databricks AI agent. **You must create your own agent** - you cannot use someone else's endpoint.

### **Steps to Create an AI Agent:**

1. **In Databricks, create:** A Genie Agent, a RAG Agent (directed at a streaming table of live industry news), and an Orchestrator agent to manage these two
2. **Create a new serving endpoint:** Create a serving endpoint for this orchestrator agent.
3. **Get the endpoint name:**
   - Once deployed, copy the endpoint name
   - Set this as `AI_AGENT_ENDPOINT` in your `app.yaml`
4. **Test the endpoint:**
   - Use the "Query" tab to verify it's working
   - Your endpoint URL will be: `https://your-workspace.azuredatabricks.net/serving-endpoints/YOUR-ENDPOINT-NAME/invocations`

> **Note:** If you don't have access to AI agents or want to skip the chatbot feature, you can:
> - Leave `AI_AGENT_ENDPOINT` as `"your-ai-agent-endpoint"` (chatbot will show an error message)
> - Comment out the chatbot section in the app layout

---

## 🗄️ Data Schema

The application expects the following tables in your Databricks schema:

### **Required Tables**

1. **`players`**
   - `player_id` (string)
   - `city` (string)
   - `country` (string)
   - `latitude` (double)
   - `longitude` (double)

2. **`sessions`**
   - `session_id` (string)
   - `player_id` (string)
   - `start_time` (timestamp)
   - `status` (string: 'completed', 'active', etc.)

### **Generate Sample Data**

Use the included data generation script:

```bash
python databricks_generate_data.py
```

This creates synthetic game analytics data for testing.

---

## 🔒 Security

**⚠️ IMPORTANT: Never commit credentials to Git!**

### **Protected Files**
The following files are automatically ignored by `.gitignore`:
- `app.yaml` (contains your actual credentials)
- `databricks_app.py` (has hardcoded values)
- `.env` files
- `setup_databricks_env.sh`

### **Safe to Commit**
- `databricks_git_app.py` ✅ (uses environment variables)
- `app.yaml.template` ✅ (placeholder values only)
- `.gitignore` ✅
- All `.md` files ✅
- `requirements.txt` ✅

### **If Credentials Leak**

1. **Immediately revoke your Databricks token**
   - Databricks → User Settings → Developer → Access Tokens → Revoke
2. **Generate a new token**
3. **See [SECURITY_GUIDE.md](SECURITY_GUIDE.md) for cleanup procedures**

---

## 📚 Documentation

- **[SECURITY_GUIDE.md](SECURITY_GUIDE.md)** - Complete security documentation
- **[ENV_VARS_NEEDED.md](ENV_VARS_NEEDED.md)** - Environment variable reference
- **[app.yaml.template](app.yaml.template)** - Configuration template

---

## 🎨 Architecture

```
┌─────────────────────────────────────────────────┐
│           Databricks Creator Hub                │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐      ┌──────────────┐       │
│  │ 3D Globe     │◄─────┤ Databricks   │       │
│  │ Visualization│      │ SQL Warehouse│       │
│  └──────────────┘      └──────────────┘       │
│         │                                       │
│         ▼                                       │
│  ┌──────────────┐      ┌──────────────┐       │
│  │ AI Chatbot   │◄─────┤ AI Agent     │       │
│  │ Interface    │      │ Endpoint     │       │
│  └──────────────┘      └──────────────┘       │
│         │                                       │
│         ▼                                       │
│  ┌──────────────┐      ┌──────────────┐       │
│  │ Embedded     │◄─────┤ AI/BI        │       │
│  │ Dashboard    │      │ Dashboard    │       │
│  └──────────────┘      └──────────────┘       │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

- **Frontend Framework**: [Dash](https://dash.plotly.com/) (Python web framework)
- **Visualization**: [Plotly](https://plotly.com/) (3D globe & charts)
- **Backend**: [Flask](https://flask.palletsprojects.com/) (via Dash)
- **Database**: [Databricks SQL](https://www.databricks.com/)
- **AI**: Databricks AI Agents
- **Deployment**: [Databricks Apps](https://docs.databricks.com/en/dev-tools/databricks-apps/)

---

## 📦 Project Structure

```
fortnite-creator-hub/
├── databricks_git_app.py       # Main application (GitHub-safe)
├── databricks_generate_data.py # Data generation script
├── app.yaml.template            # Configuration template
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
├── SECURITY_GUIDE.md            # Security documentation
└── ENV_VARS_NEEDED.md          # Environment variable guide
```

---

## 🎮 Features in Detail

### **Globe Visualization**
- **Technology**: Plotly Scattergeo with orthographic projection
- **Update Frequency**: Every 5 minutes
- **Rotation Speed**: 1.5° per frame (100ms intervals)
- **Color Scale**: Blue (low activity) → Pink → Orange (high activity)
- **Interactive**: Pan to explore, auto-resumes rotation

### **AI Chatbot**
- **Model**: Databricks AI Agent (customizable)
- **Features**: 
  - Conversation memory
  - Markdown rendering
  - Loading indicators
  - Error handling with user-friendly messages
- **Key Insights**: Auto-generated weekly summaries on app load

### **Analytics Dashboard**
- **Embedded via iframe**: Databricks AI/BI dashboards
- **Customizable**: Replace with your own dashboard ID
- **Responsive**: Full-width, 1000px height

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Note**: Never commit credentials or sensitive data!

---

## 📝 License

This project is provided as-is for educational and demonstration purposes.

---

## 🆘 Support

- **Documentation**: Check [SECURITY_GUIDE.md](SECURITY_GUIDE.md) and [ENV_VARS_NEEDED.md](ENV_VARS_NEEDED.md)
- **Issues**: Open an issue on GitHub
- **Databricks**: [Databricks Apps Documentation](https://docs.databricks.com/en/dev-tools/databricks-apps/)

---

## 🌟 Acknowledgments

- Built for Fortnite Creative map analytics
- Powered by Databricks
- Styled with Fortnite's vibrant color palette

---

<div align="center">

**Made with ⚡ by [Your Name]**

[⬆ Back to Top](#-fortnite-creator-hub---player-analytics-dashboard)

</div>
