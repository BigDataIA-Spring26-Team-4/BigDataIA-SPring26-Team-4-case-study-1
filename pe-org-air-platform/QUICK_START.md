# ⚡ QUICK START - Do This Now!

## 🎯 Step 1: Install Poetry (if not already installed)

**Windows PowerShell (as Admin):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

**Close and reopen your terminal**, then verify:
```bash
poetry --version
```

---

## 🎯 Step 2: Setup Project

```bash
# Navigate to project
cd D:\DAMG7245_Big_Data_Systems\BigDataIA-SPring26-Team-4-case-study-1\pe-org-air-platform

# Install all dependencies (this creates .venv folder)
poetry install

# This will take 2-3 minutes...
```

---

## 🎯 Step 3: Configure Environment

```bash
# Copy template
copy .env.example .env

# Edit .env file with YOUR Snowflake credentials
# Open in VS Code or any editor
```

**Required in .env:**
```env
SNOWFLAKE_ACCOUNT=your_account.region.cloud
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
```

---

## 🎯 Step 4: Start Redis (Docker)

```bash
docker run -d --name redis-pe-org-air -p 6379:6379 redis:7-alpine
```

---

## 🎯 Step 5: Open in VS Code

```bash
# From the root of the repo
code .
```

**In VS Code:**
1. Open Command Palette (`Ctrl+Shift+P`)
2. Type: "Python: Select Interpreter"
3. Choose: `.venv\Scripts\python.exe` from pe-org-air-platform

---

## 🎯 Step 6: Test Configuration

```bash
# Activate poetry shell
poetry shell

# Test imports
python -c "from app.config import settings; print(f'✅ Config loaded: {settings.APP_NAME}')"

# Should output: ✅ Config loaded: PE Org-AI-R Platform
```

---

## 🎯 Step 7: What's Next?

Tell me when you complete steps 1-6, and I'll help you:

1. ✅ Create database initialization script
2. ✅ Update Snowflake service to use new models
3. ✅ Implement proper Redis caching
4. ✅ Update all routers
5. ✅ Add pagination
6. ✅ Create health check with dependency checks
7. ✅ Update Docker configuration
8. ✅ Run tests

---

## ⚠️ Common Issues

**Poetry command not found after install:**
- Close and reopen terminal
- Or add Poetry to PATH manually

**Python version mismatch:**
```bash
poetry env use python3.11
poetry install
```

**Redis connection error:**
```bash
docker ps  # Check if Redis is running
```

---

## 📞 Ready?

Once you've done steps 1-6, message me with:
- "Poetry setup done, ready to continue!"
- Or any error messages you see

Then we'll build the services together! 🚀
