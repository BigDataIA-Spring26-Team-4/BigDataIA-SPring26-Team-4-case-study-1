# PE Org-AI-R Platform - Complete Setup Guide

## 🚀 Quick Start

### 1. Open Project in VS Code
```bash
cd D:\DAMG7245_Big_Data_Systems\BigDataIA-SPring26-Team-4-case-study-1
code .
```

### 2. Create Python Virtual Environment
```bash
# In VS Code terminal (Ctrl + `)
cd pe-org-air-platform
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy the example file
copy .env.example .env

# Edit .env with your actual credentials
# Use VS Code to open and edit the .env file
```

### 5. Set Up Snowflake Database
```bash
# We'll provide a Python script to run the schema
# This will be created in the next steps
```

### 6. Run the Application

#### Option A: Local Development (Recommended for development)
```bash
# Make sure you're in pe-org-air-platform directory
# Make sure venv is activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Option B: Docker (Production-like)
```bash
# Build and run with Docker Compose
docker-compose -f docker/compose.yaml up --build
```

### 7. Test the API
Open browser: http://localhost:8000/docs
(This opens the interactive Swagger UI)

---

## 📁 VS Code Recommended Extensions

Install these for better development experience:
1. **Python** (Microsoft)
2. **Pylance** (Microsoft)
3. **Docker** (Microsoft)
4. **GitLens** (GitKraken)
5. **Thunder Client** or **REST Client** (for API testing)
6. **Better Comments** (for better code readability)

---

## 🔧 VS Code Settings

Create `.vscode/settings.json` in your project root for consistent formatting:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/pe-org-air-platform/venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
```

---

## 🎯 Next Steps

After setup:
1. ✅ Models are properly defined (Company, Assessment, DimensionScore)
2. ✅ Config management is robust
3. ✅ Database connection works
4. ✅ Redis caching works
5. ✅ S3 storage works
6. ✅ All API endpoints work
7. ✅ Tests pass
8. ✅ Docker builds successfully

---

## 🆘 Troubleshooting

### Virtual Environment Issues
```bash
# If venv activation fails, try:
python -m venv venv --clear
```

### Package Installation Issues
```bash
# If pip install fails:
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Snowflake Connection Issues
- Verify your account identifier format
- Check username/password
- Ensure warehouse is running
- Verify network connectivity

### Docker Issues
```bash
# Clean up Docker
docker system prune -a
docker-compose down -v
```
