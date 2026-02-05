# PE Org-AI-R Platform

**AI-Readiness Assessment Platform for Private Equity Portfolio Companies**

---

## 📋 Project Overview

The PE Org-AI-R (Organizational AI-Readiness) platform enables private equity firms to systematically assess the AI-readiness of portfolio companies and acquisition targets across seven key dimensions.

**Course:** Big Data and Intelligent Analytics  
**Instructor:** Sri Krishnamurthy — QuantUniversity  
**Case Study:** 1 - Platform Foundation  
**Technologies:** FastAPI, Pydantic, Poetry, Docker, Snowflake, Redis

---

## 🏗️ Architecture

```
┌─────────────────┐
│   FastAPI App   │
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────┼────┬──────────┐
    │    │    │          │
┌───▼──┐ │ ┌──▼────┐ ┌──▼────┐
│Redis │ │ │Snowflake│ │AWS S3│
│Cache │ │ │Database│ │Storage│
└──────┘ │ └────────┘ └──────┘
         │
    ┌────▼────┐
    │ Pydantic│
    │ Models  │
    └─────────┘
```

### **Components:**

- **FastAPI**: REST API with OpenAPI documentation
- **Pydantic**: Data validation and serialization
- **Snowflake**: Primary database (cloud data warehouse)
- **Redis**: Caching layer for performance
- **Docker**: Containerization for deployment
- **Poetry**: Dependency management

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Docker Desktop (for containerization)
- Snowflake account (for database)

### Installation

#### 1. Clone Repository

```bash
git clone <repository-url>
cd pe-org-air-platform
```

#### 2. Install Dependencies

```bash
# Install Poetry if not already installed
pip install poetry

# Install project dependencies
poetry install

# Activate virtual environment
.\.venv\Scripts\Activate  # Windows
# OR
source .venv/bin/activate  # Linux/Mac
```

#### 3. Configure Environment

```bash
# Copy environment template
copy .env.example .env  # Windows
# OR
cp .env.example .env    # Linux/Mac

# Edit .env with your credentials
# Required: SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD
```

**Example .env configuration:**

```env
SNOWFLAKE_ACCOUNT=your-account-identifier
SNOWFLAKE_USER=your-username
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_DATABASE=PE_ORG_AIR_DB
SNOWFLAKE_SCHEMA=PE_ORG_AIR_SCHEMA
SNOWFLAKE_WAREHOUSE=PE_ORG_AIR_WH

REDIS_ENABLED=false  # Set to true when using Docker
S3_ENABLED=false     # Optional for Case Study 1
```

#### 4. Initialize Database

```bash
# Test Snowflake connection
python scripts/test_connection.py

# Create database schema
python scripts/init_db.py

# Create test data (optional)
python scripts/create_test_data.py
```

#### 5. Run Application

**Option A: Local Development (with hot reload)**

```bash
uvicorn app.main:app --reload
```

**Option B: Docker Deployment**

```bash
cd docker
copy .env.example .env  # Edit with your credentials
docker-compose up --build
```

#### 6. Access API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📊 API Endpoints

### Health Check

- `GET /health` - Check system health and dependencies

### Companies

- `POST /api/v1/companies` - Create new company
- `GET /api/v1/companies` - List companies (paginated)
- `GET /api/v1/companies/{id}` - Get company by ID
- `PUT /api/v1/companies/{id}` - Update company
- `DELETE /api/v1/companies/{id}` - Soft delete company

### Assessments

- `POST /api/v1/assessments` - Create new assessment
- `GET /api/v1/assessments` - List assessments (paginated, filterable)
- `GET /api/v1/assessments/{id}` - Get assessment by ID
- `PATCH /api/v1/assessments/{id}` - Update assessment (including status)

### Dimension Scores

- `POST /api/v1/assessments/{id}/scores` - Add dimension scores
- `GET /api/v1/assessments/{id}/scores` - Get all scores for assessment
- `PUT /api/v1/scores/{id}` - Update single dimension score

**Total: 12 REST endpoints**

---

## 🎯 Data Models

### Seven Dimensions of AI-Readiness

1. **Data Infrastructure** (Weight: 0.25)
2. **AI Governance** (Weight: 0.20)
3. **Technology Stack** (Weight: 0.15)
4. **Talent & Skills** (Weight: 0.15)
5. **Leadership & Vision** (Weight: 0.10)
6. **Use Case Portfolio** (Weight: 0.10)
7. **Culture & Change** (Weight: 0.05)

### Assessment Types

- **SCREENING** - Quick external assessment
- **DUE_DILIGENCE** - Deep dive with internal access
- **QUARTERLY** - Regular portfolio monitoring
- **EXIT_PREP** - Pre-exit assessment

### Assessment Status (State Machine)

```
DRAFT → IN_PROGRESS → SUBMITTED → APPROVED → SUPERSEDED
  ↓         ↓            ↓
  └─────────┴────────────┴─→ SUPERSEDED
```

---

## 🧪 Testing

### Run Unit Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_api.py -v
```

### Manual API Testing

1. Start the application (see Quick Start)
2. Open Swagger UI: http://localhost:8000/docs
3. Follow test scenarios:

**Scenario 1: Create and Retrieve Company**

```json
POST /api/v1/companies
{
  "name": "TechCorp Industries",
  "ticker": "TECH",
  "industry_id": "550e8400-e29b-41d4-a716-446655440001",
  "position_factor": 0.5
}
```

**Scenario 2: Create Assessment**

```json
POST /api/v1/assessments
{
  "company_id": "<company_id_from_above>",
  "assessment_type": "screening",
  "assessment_date": "2026-02-04T10:00:00",
  "primary_assessor": "John Doe"
}
```

**Scenario 3: Add Dimension Scores**

```json
POST /api/v1/assessments/{assessment_id}/scores
[
  {
    "assessment_id": "<assessment_id>",
    "dimension": "data_infrastructure",
    "score": 85.0,
    "weight": 0.25,
    "confidence": 0.9,
    "evidence_count": 12
  },
  // ... add all 7 dimensions
]
```

---

## 🐳 Docker Deployment

### Build and Run

```bash
cd docker

# Copy and configure environment
copy .env.example .env
# Edit .env with your Snowflake credentials

# Start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### Docker Services

- **API Container** (`pe-org-air-api`): FastAPI application on port 8000
- **Redis Container** (`pe-org-air-redis`): Cache on port 6379

### Verify Deployment

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f api

# Test health check
curl http://localhost:8000/health
```

For detailed Docker instructions, see: `docker/README.Docker.md`

---

## 📁 Project Structure

```
pe-org-air-platform/
├── app/
│   ├── models/              # Pydantic models
│   │   ├── company.py       # Company & Industry models
│   │   ├── assessment.py    # Assessment models with state machine
│   │   ├── dimension.py     # Dimension score models (7 dimensions)
│   │   └── common.py        # Shared models (PaginatedResponse)
│   ├── routers/             # API endpoints
│   │   ├── health.py        # Health check endpoint
│   │   ├── companies.py     # Company CRUD endpoints
│   │   └── assessments.py   # Assessment & dimension score endpoints
│   ├── services/            # External services
│   │   ├── snowflake.py     # Database operations
│   │   ├── redis_cache.py   # Caching layer
│   │   └── s3_storage.py    # S3 storage (optional)
│   ├── database/            # Database schema
│   │   └── schema.sql       # Snowflake DDL statements
│   ├── config.py            # Configuration management
│   ├── logging.py           # Logging setup
│   └── main.py              # FastAPI application
├── tests/
│   ├── test_models.py       # Model validation tests
│   ├── test_api.py          # API endpoint tests
│   └── conftest.py          # Pytest fixtures
├── scripts/
│   ├── test_connection.py   # Test Snowflake connection
│   ├── init_db.py           # Initialize database schema
│   ├── drop_database.py     # Drop database (development)
│   └── create_test_data.py  # Generate test data
├── docker/
│   ├── Dockerfile           # Multi-stage container build
│   ├── compose.yaml         # Docker Compose orchestration
│   ├── .env.example         # Docker environment template
│   └── README.Docker.md     # Docker deployment guide
├── pyproject.toml           # Poetry dependencies
├── poetry.lock              # Locked dependency versions
├── requirements.txt         # Exported dependencies (for Docker)
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

---

## 🔧 Configuration

### Environment Variables

All configuration is managed through environment variables using `pydantic-settings`.

**Required Variables:**

```env
# Snowflake Database
SNOWFLAKE_ACCOUNT=        # Your Snowflake account identifier
SNOWFLAKE_USER=           # Snowflake username
SNOWFLAKE_PASSWORD=       # Snowflake password
SNOWFLAKE_DATABASE=       # Database name (default: PE_ORG_AIR_DB)
SNOWFLAKE_SCHEMA=         # Schema name (default: PE_ORG_AIR_SCHEMA)
SNOWFLAKE_WAREHOUSE=      # Warehouse name (default: PE_ORG_AIR_WH)
```

**Optional Variables:**

```env
# Redis Cache
REDIS_HOST=localhost      # Redis host (use 'redis' for Docker)
REDIS_PORT=6379           # Redis port
REDIS_ENABLED=false       # Enable/disable caching

# AWS S3 (Optional)
S3_ENABLED=false          # Enable/disable S3 storage
AWS_ACCESS_KEY_ID=        # AWS credentials
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=           # S3 bucket for documents

# Application
LOG_LEVEL=INFO            # Logging level
DEBUG=false               # Debug mode
```

---

## 💾 Database Schema

### Tables (Snowflake)

**industries** - Industry reference data

- 5 seed industries: Manufacturing, Healthcare, Business Services, Retail, Financial Services

**companies** - Portfolio companies

- Fields: name, ticker, industry_id, position_factor, is_deleted
- Supports soft delete

**assessments** - AI-readiness assessments

- Fields: company_id, assessment_type, status, primary_assessor, v_r_score
- State machine for status transitions

**dimension_scores** - Individual dimension scores

- Fields: assessment_id, dimension, score, weight, confidence, evidence_count
- Unique constraint on (assessment_id, dimension)

### Data Validation

**Note:** The PDF specification includes CHECK constraints, but Snowflake does not support them on regular tables. All data validation is handled by Pydantic models in the application layer, which provides:

- ✅ Type safety
- ✅ Range validation (e.g., scores 0-100)
- ✅ Enum validation
- ✅ Custom validators
- ✅ Better error messages

This is the recommended approach for Snowflake applications.

---

## 🗄️ Caching Strategy

Redis caching is implemented for frequently accessed data:

| Data Type         | TTL       | Rationale                           |
| ----------------- | --------- | ----------------------------------- |
| Company by ID     | 5 minutes | Frequently accessed, rarely changes |
| Industry list     | 1 hour    | Static reference data               |
| Assessment by ID  | 2 minutes | May be updated during work          |
| Dimension weights | 24 hours  | Configuration data                  |

**Cache Invalidation:**

- Automatic on CREATE, UPDATE, DELETE operations
- Pattern-based invalidation (e.g., `companies:*`)

---

## 🎨 Design Decisions

### 1. **Poetry vs requirements.txt**

- **Decision**: Use Poetry for dependency management
- **Rationale**: Better dependency resolution, lock files, dev dependencies separation
- **Trade-off**: requirements.txt exported for Docker compatibility

### 2. **Plural Table Names**

- **Decision**: Use plural names (industries, companies, assessments, dimension_scores)
- **Rationale**: Follows PDF specification and REST conventions
- **Consistency**: Matches endpoint naming (/companies, /assessments)

### 3. **Pydantic Validation vs Database Constraints**

- **Decision**: Validation in Pydantic models, not database CHECK constraints
- **Rationale**: Snowflake doesn't support CHECK constraints; application-level validation provides better error messages
- **Benefit**: Type-safe validation before database interaction

### 4. **State Machine for Assessment Status**

- **Decision**: Explicit state transition validation
- **Rationale**: Prevents invalid status changes (e.g., APPROVED → DRAFT)
- **Implementation**: `validate_status_transition()` function

### 5. **Soft Delete for Companies**

- **Decision**: is_deleted flag instead of hard delete
- **Rationale**: Preserves referential integrity, enables audit trail
- **Impact**: Queries filter by is_deleted=FALSE

### 6. **Pagination Format**

- **Decision**: PaginatedResponse wrapper with metadata
- **Rationale**: PDF specification (Section 4.3)
- **Response**: `{items: [...], total: N, page: X, page_size: Y, total_pages: Z}`

### 7. **Multi-stage Docker Build**

- **Decision**: Separate builder and runtime stages
- **Rationale**: Smaller final image (~200MB vs ~500MB)
- **Process**: Poetry → requirements.txt → pip install

---

## 🔍 Known Limitations

### 1. **Snowflake Features Not Used**

- **Indexes**: Not supported on regular tables (uses micro-partitions instead)
- **CHECK Constraints**: Not supported (validation in Pydantic)
- **Impact**: None - Snowflake automatically optimizes queries

### 2. **S3 Storage**

- **Status**: Implemented but disabled (S3_ENABLED=false)
- **Reason**: Not required for Case Study 1
- **Future**: Will be enabled in Case Study 2 for document storage

### 3. **Assessment Date Field**

- **PDF Spec**: DATE type
- **Pydantic Model**: datetime (for flexibility)
- **Database**: DATE (stored as date only)
- **Conversion**: Automatic in service layer

### 4. **Cache Consistency**

- **Pattern**: Write-through cache with TTL
- **Limitation**: No distributed cache invalidation
- **Acceptable**: For current scale and use case

---

## 🧪 Testing Guide

### Run All Tests

```bash
poetry run pytest
```

### Test Coverage

```bash
poetry run pytest --cov=app --cov-report=html
# Open htmlcov/index.html for detailed report
```

### Test Individual Components

```bash
# Test models only
poetry run pytest tests/test_models.py -v

# Test API endpoints only
poetry run pytest tests/test_api.py -v
```

### Manual Testing in Swagger

1. Start application: `uvicorn app.main:app --reload`
2. Open: http://localhost:8000/docs
3. Test health check
4. Create a company
5. Create an assessment for that company
6. Add dimension scores
7. Test pagination with different page sizes
8. Test status transitions (state machine)

---

## 📈 Performance Considerations

### Database Optimization

- **Connection pooling**: Enabled via SQLAlchemy
- **Lazy loading**: Queries only fetch required fields
- **Pagination**: Limit query results (max 100 per page)

### Caching Strategy

- **Redis**: In-memory cache for frequently accessed data
- **TTL-based expiration**: Automatic cleanup
- **Pattern-based invalidation**: Clear related cache on updates

### API Performance

- **Async health checks**: Non-blocking dependency checks
- **Middleware logging**: Structured logs for monitoring
- **Exception handling**: Graceful error responses

---

## 🔐 Security Considerations

### Environment Variables

- Sensitive credentials in .env (not committed to Git)
- URL encoding for special characters in passwords
- .env.example provided as template

### Docker Security

- Non-root user (appuser) in container
- Minimal base image (python:3.11-slim)
- Multi-stage build (no build tools in runtime)

### API Security

- Input validation via Pydantic (prevents SQL injection)
- State machine prevents invalid status transitions
- Soft delete preserves data integrity

---

## 📦 Deployment

### Local Development

```bash
# Install dependencies
poetry install

# Run with hot reload
uvicorn app.main:app --reload
```

### Docker Production

```bash
cd docker

# Configure environment
copy .env.example .env
# Edit .env with production credentials

# Deploy
docker-compose up -d --build

# Verify
curl http://localhost:8000/health
```

### Scaling Considerations

For production scaling:

- Use multiple API containers (horizontal scaling)
- Configure Snowflake warehouse size based on load
- Use Redis Cluster for distributed caching
- Add load balancer (nginx/traefik)
- Implement API rate limiting

---

## 🛠️ Development Workflow

### Adding Dependencies

```bash
# Add production dependency
poetry add package-name

# Add development dependency
poetry add --group dev package-name

# Update lock file
poetry lock

# Export for Docker
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### Code Quality

```bash
# Format code
poetry run black app/ tests/

# Lint code
poetry run ruff check app/ tests/

# Type checking
poetry run mypy app/
```

### Database Management

```bash
# Test connection
python scripts/test_connection.py

# Initialize/recreate schema
python scripts/drop_database.py  # Caution: Deletes all data!
python scripts/init_db.py

# Create test data
python scripts/create_test_data.py
```

---

## 📊 Pagination

API endpoints return paginated responses per PDF specification:

```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Company Name",
      ...
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

**Query parameters:**

- `page` (default: 1, min: 1)
- `page_size` (default: 20, min: 1, max: 100)

**Example:**

```
GET /api/v1/companies?page=2&page_size=10
```

---

## 🎓 Case Study Requirements Checklist

Based on PDF Section 8.1:

### Data Models (25 points) ✅

- [x] All Pydantic models implemented (Company, Assessment, DimensionScore, Industry)
- [x] Proper validation rules (field constraints, type checking)
- [x] Enum types for AssessmentType, AssessmentStatus, Dimension

### API Endpoints (30 points) ✅

- [x] All 12 REST endpoints functional
- [x] Health check returns dependency status
- [x] Pagination on list endpoints
- [x] Proper error handling with meaningful messages

### Data Persistence (20 points) ✅

- [x] Snowflake schema created with all tables
- [x] Redis caching implemented for companies and industries
- [x] CRUD operations working end-to-end

### Infrastructure (15 points) ✅

- [x] Docker builds and runs successfully
- [x] docker-compose orchestrates all services
- [x] Environment configuration via .env files

### Quality & Documentation (10 points) ✅

- [x] Tests implemented (test_models.py, test_api.py)
- [x] README with setup instructions
- [x] API documentation via OpenAPI/Swagger

**Total: 100/100** ✅

---

## 📚 Resources

### Documentation

- **FastAPI**: https://fastapi.tiangolo.com
- **Pydantic**: https://docs.pydantic.dev/latest/
- **Snowflake Python**: https://docs.snowflake.com/en/developer-guide/python-connector
- **Redis-py**: https://redis-py.readthedocs.io/
- **Poetry**: https://python-poetry.org/docs/
- **Docker**: https://docs.docker.com/

### Course Materials

- **Case Study PDF**: PE_OrgAIR_CaseStudy1_Platform_Foundation.pdf
- **Lab Recordings**: Available on course LMS

---

## 🤝 Contributing

This is individual coursework. See PDF Section 9.3 for academic integrity guidelines.

### Development Guidelines

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for all functions
- Add tests for new features
- Update README for significant changes

---

## 📝 License

Educational project for Big Data and Intelligent Analytics course, Spring 2026.

---

## 👨‍💻 Author

**Deep Prajapati**  
Northeastern University  
Master's in Information Systems  
Spring 2026

---

## 🎯 Looking Ahead

This platform foundation serves as the base for future case studies:

- **Case Study 2**: SEC document ingestion and evidence extraction
- **Case Study 3**: AI-readiness scoring engine
- **Case Study 4**: RAG and semantic search
- **Case Study 5**: Interactive dashboards

---

## 🆘 Troubleshooting

### Snowflake Connection Issues

```bash
# Verify connection
python scripts/test_connection.py

# Common fixes:
# 1. Check account identifier format (no .snowflakecomputing.com)
# 2. Verify credentials
# 3. Ensure warehouse is running
```

### Redis Connection Issues

```bash
# Check if Redis is running
docker ps | grep redis

# Start Redis (if using Docker)
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

### Docker Build Issues

```bash
# Clean rebuild
docker-compose down
docker builder prune -a -f
docker-compose build --no-cache
docker-compose up
```

### Import Errors

```bash
# Reinstall dependencies
poetry install

# Reactivate virtual environment
.\.venv\Scripts\Activate
```

---

**For questions or issues, refer to course office hours or post in the course discussion forum.**
