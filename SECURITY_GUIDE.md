# 🔒 Security Guide for GitHub

## ⚠️ CRITICAL: Files to NEVER Commit

The following files contain **LIVE CREDENTIALS** and should **NEVER** be committed to Git:

### 🚨 Sensitive Files (Already in `.gitignore`)

1. **`app.yaml`** - Contains Databricks token and connection details
2. **`setup_databricks_env.sh`** - Contains exported credentials
3. **`.env`** - Any environment variable files
4. **`*.env`** - Any environment variable files with different extensions

These files are **automatically ignored** by `.gitignore`.

---

## ✅ Safe Files for GitHub

### **Application Code**
- ✅ `databricks_git_app.py` - **GitHub-safe version** (uses environment variables)
- ✅ `databricks_generate_data.py` - Data generation script
- ✅ `databricks_globe_visualization.py` - Visualization notebook
- ✅ All other `.py` files without hardcoded credentials

### **Configuration Templates**
- ✅ `app.yaml.template` - Template with placeholder values
- ✅ `env.template` - Environment variable template
- ✅ `.gitignore` - Git ignore rules

### **Documentation**
- ✅ All `.md` files (README, guides, changelogs)
- ✅ `requirements.txt` - Python dependencies

---

## 🔧 Setup Instructions for New Developers

If someone clones your repository, here's how they should set it up:

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <repo-directory>
```

### 2. Create Configuration from Templates

**Option A: Using `app.yaml` (for Databricks Apps)**
```bash
# Copy the template
cp app.yaml.template app.yaml

# Edit with your credentials
nano app.yaml  # or use your preferred editor
```

**Option B: Using `.env` file (for local development)**
```bash
# Copy the template
cp env.template .env

# Edit with your credentials
nano .env  # or use your preferred editor
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application

**For Databricks Apps:**
- Upload `databricks_git_app.py` and your `app.yaml` to Databricks
- Deploy via Databricks Apps UI or CLI

**For Local Testing:**
```bash
# Load environment variables
source .env  # Linux/Mac
# or
set -a; source .env; set +a  # Linux/Mac (alternative)

# Run the app
python databricks_git_app.py
```

---

## 🔐 Environment Variables Required

Your configuration file (`app.yaml` or `.env`) must include:

### **Required Variables:**
- `DATABRICKS_SERVER_HOSTNAME` - Your Databricks workspace URL
- `DATABRICKS_HTTP_PATH` - SQL Warehouse connection path
- `DATABRICKS_TOKEN` - Personal Access Token
- `DATABRICKS_SCHEMA` - Schema name (e.g., `catalog.schema`)

### **Optional Variables:**
- `AI_AGENT_ENDPOINT` - AI serving endpoint name (for chatbot)
- `DATABRICKS_DASHBOARD_ID` - Dashboard ID (for embedded analytics)
- `DATABRICKS_WORKSPACE_ID` - Workspace ID (usually auto-extracted)

### **Where to Find These Values:**

| Variable | Where to Find |
|----------|---------------|
| `DATABRICKS_SERVER_HOSTNAME` | Browser URL when logged into Databricks |
| `DATABRICKS_HTTP_PATH` | SQL Warehouses → Your Warehouse → Connection Details |
| `DATABRICKS_TOKEN` | User Settings → Developer → Access Tokens → Generate New Token |
| `DATABRICKS_SCHEMA` | Data Explorer in Databricks |
| `AI_AGENT_ENDPOINT` | Machine Learning → Serving → Your Endpoint |
| `DATABRICKS_DASHBOARD_ID` | Dashboards → Share → Embed → Copy ID from URL |

---

## 🚨 If You Accidentally Committed Credentials

If you've already pushed credentials to GitHub:

### 1. **IMMEDIATELY Revoke the Token**
- Go to Databricks → User Settings → Developer → Access Tokens
- Find and revoke the exposed token
- Generate a new token

### 2. **Remove from Git History**

**Option A: Delete and Recreate Repository (Simplest)**
```bash
# Delete the repo on GitHub
# Create a new empty repo
# Re-commit only safe files

git init
git add databricks_git_app.py app.yaml.template .gitignore requirements.txt *.md
git commit -m "Initial commit with secure configuration"
git remote add origin <new-repo-url>
git push -u origin main
```

**Option B: Use BFG Repo-Cleaner (Advanced)**
```bash
# Install BFG Repo-Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/

# Remove sensitive files from history
bfg --delete-files app.yaml
bfg --delete-files setup_databricks_env.sh

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (⚠️ WARNING: This rewrites history!)
git push origin --force --all
```

---

## ✅ Pre-Commit Checklist

Before committing code, always verify:

- [ ] No hardcoded credentials in any `.py` files
- [ ] All sensitive data uses environment variables
- [ ] `.gitignore` is present and up-to-date
- [ ] `app.yaml` is NOT staged for commit
- [ ] `.env` files are NOT staged for commit
- [ ] Only `app.yaml.template` is committed, not `app.yaml`

**Check what you're about to commit:**
```bash
git status
git diff --staged
```

**If you see `app.yaml` or `.env` in the list:**
```bash
git reset app.yaml    # Unstage the file
git reset .env        # Unstage the file
```

---

## 🛡️ Best Practices

1. **Use Templates:**
   - Always commit `.template` files, not actual config files
   - Templates should have `your-value-here` placeholders

2. **Environment Variables:**
   - Prefer environment variables over hardcoded values
   - Use `os.getenv()` with sensible defaults

3. **Regular Audits:**
   - Periodically rotate your Databricks tokens
   - Review `.gitignore` to ensure it's comprehensive

4. **Team Communication:**
   - Document all required environment variables
   - Share secure credentials through secure channels (not Git!)
   - Use secret management tools for teams (e.g., AWS Secrets Manager, HashiCorp Vault)

5. **GitHub Secrets:**
   - For CI/CD, use GitHub Secrets instead of environment files
   - Navigate to: Repository → Settings → Secrets and variables → Actions

---

## 📚 Additional Resources

- [GitHub: Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [Databricks: Personal Access Tokens](https://docs.databricks.com/dev-tools/auth/pat.html)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [Git: .gitignore patterns](https://git-scm.com/docs/gitignore)

---

## 🆘 Need Help?

If you're unsure whether something is safe to commit:

1. **Check if it contains:**
   - API tokens or passwords
   - Server hostnames with workspace IDs
   - Database connection strings
   - Any value that starts with `dapi...`

2. **When in doubt:** DON'T COMMIT IT!
   - Use templates instead
   - Store in environment variables
   - Document in the README how to obtain the value

---

**Remember:** It's much easier to prevent credential exposure than to clean it up after the fact! 🔐

