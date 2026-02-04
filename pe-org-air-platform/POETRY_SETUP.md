# PE Org-AI-R Platform Setup Guide (Poetry Edition)

## 🚀 Quick Start with Poetry

### Prerequisites
- Python 3.11+
- Poetry installed (`pip install poetry` or use official installer)
- Snowflake account credentials
- Docker Desktop (for Redis)

---

## Step-by-Step Setup

### 1️⃣ Install Dependencies

```bash
cd pe-org-air-platform

# Install all dependencies (creates .venv automatically)
poetry install

# Activate poetry shell
poetry shell
```

### 2️⃣ Configure Environment

```bash
# Copy example env file
copy .env.example .env

# Edit .env with your actual Snowflake credentials
# Use any text editor or VS Code
```

**Required values in .env:**
```env
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=PE_ORG_AIR_DB
SNOWFLAKE_SCHEMA=PE_ORG_AIR_SCHEMA
SNOWFLAKE_WAREHOUSE=PE_ORG_AIR_WH

# For local dev (Redis will be in Docker)
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 3️⃣ Start Redis with Docker

```bash
# In a separate terminal
docker run -d --name redis-pe-org-air -p 6379:6379 redis:7-alpine

# Verify it's running
docker ps
```

### 4️⃣ Initialize Snowflake Database

```bash
# We'll create a script for this
poetry run python scripts/init_db.py
```

### 5️⃣ Run the Application

**Option A: Development Mode (with hot reload)**
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option B: Using Poetry script**
```bash
poetry run start
```

**Option C: Inside Poetry shell**
```bash
poetry shell
uvicorn app.main:app --reload
```

### 6️⃣ Test the API

Open browser: http://localhost:8000/docs

---

## 🧪 Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_models.py

# Run with verbose output
poetry run pytest -v
```

---

## 🛠️ Development Workflow

### Adding New Dependencies

```bash
# Add a production dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name

# Update dependencies
poetry update
```

### Code Formatting & Linting

```bash
# Format code with Black
poetry run black app/ tests/

# Lint with Ruff
poetry run ruff check app/ tests/

# Type checking with mypy
poetry run mypy app/
```

### Working with Poetry Shell

```bash
# Enter poetry shell (activates .venv)
poetry shell

# Now you can run commands directly:
uvicorn app.main:app --reload
pytest
black app/

# Exit poetry shell
exit
```

---

## 🐳 Docker Development

### Start Everything with Docker Compose

```bash
cd docker
docker-compose up --build
```

This will start:
- FastAPI application
- Redis cache
- All services configured

---

## 📁 Project Structure

```
pe-org-air-platform/
├── .venv/                    # Poetry virtual environment (auto-created)
├── app/
│   ├── models/              # Pydantic models (✅ Done)
│   ├── routers/             # API endpoints
│   ├── services/            # External services (Snowflake, Redis, S3)
│   ├── config.py            # Pydantic Settings (✅ Done)
│   └── main.py              # FastAPI app
├── tests/
├── docker/
├── pyproject.toml           # Poetry config (✅ Done)
├── poetry.toml              # Poetry settings (✅ Done)
├── .env                     # Your secrets (not in git)
└── .env.example             # Template (✅ Done)
```

---

## 🎯 Key Poetry Commands

```bash
# Show current environment
poetry env info

# List installed packages
poetry show

# Update a specific package
poetry update package-name

# Remove a package
poetry remove package-name

# Export requirements.txt (if needed)
poetry export -f requirements.txt --output requirements.txt

# Run any command in poetry environment
poetry run <command>
```

---

## ✅ Verify Setup

After setup, verify everything works:

```bash
# 1. Check Python environment
poetry run python --version

# 2. Check imports work
poetry run python -c "from app.config import settings; print(settings.APP_NAME)"

# 3. Check Snowflake connection
poetry run python -c "from app.services.snowflake import engine; print(engine)"

# 4. Run tests
poetry run pytest

# 5. Start application
poetry run uvicorn app.main:app --reload
```

---

## 🆘 Troubleshooting

### Poetry not found
```bash
# Windows PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Restart terminal
```

### Wrong Python version
```bash
# Tell Poetry which Python to use
poetry env use python3.11
poetry install
```

### Redis connection failed
```bash
# Check if Redis is running
docker ps | grep redis

# Start Redis if not running
docker run -d --name redis-pe-org-air -p 6379:6379 redis:7-alpine
```

### Snowflake connection failed
```bash
# Verify credentials in .env
# Make sure warehouse is running in Snowflake console
# Check account format: account.region (e.g., xy12345.us-east-1)
```

---

## 📚 Resources

- **Poetry**: https://python-poetry.org/docs/
- **Pydantic Settings**: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Snowflake Python**: https://docs.snowflake.com/en/developer-guide/python-connector/python-connector
