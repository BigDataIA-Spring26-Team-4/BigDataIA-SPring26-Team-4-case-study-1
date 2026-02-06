# PE Org-AIR Platform - Platform Foundation

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Educational-orange.svg)](LICENSE)

## 📚 Important Links

- **Codelabs Document**: <Codelabs link>
- **Video Presentation**: <Video presentation link>
- **Live Application**: <Streamlit/FastAPI application URL>
- **API Documentation**: http://localhost:8000/docs (when running locally)
- **GitHub Repository**: <GitHub repository link>

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Directory Structure](#directory-structure)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Running Tests](#running-tests)
- [Team Contributions](#team-contributions)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## Project Overview

The **PE Org-AIR (Organizational AI-Readiness) Platform** is a comprehensive data-driven system designed for private equity firms to systematically assess the AI-readiness of portfolio companies and acquisition targets.

### Purpose

Private equity firms need to evaluate potential investments and portfolio companies across multiple dimensions to understand their readiness to adopt and benefit from AI technologies. This platform provides:

- **Standardized Assessment Framework**: Seven-dimension evaluation model for consistent comparison
- **Data-Driven Insights**: Integration with Snowflake for advanced analytics and reporting
- **Real-Time Caching**: Redis-powered caching for high-performance API responses
- **RESTful API**: Modern FastAPI-based backend with comprehensive CRUD operations
- **Scalable Architecture**: Docker-based containerization for easy deployment and scaling

### Scope

**Case Study 1** establishes the platform foundation with:
- Complete RESTful API with 17+ endpoints
- Full CRUD operations for Industries, Companies, Assessments, and Dimension Scores
- Pydantic-based data validation and serialization
- Redis caching layer with intelligent TTL management
- Snowflake data warehouse integration
- Comprehensive test suite with pytest
- Docker containerization for consistent environments

**Future Case Studies** will extend functionality with:
- SEC filing ingestion and AI evidence extraction
- Automated scoring engine with VR (Value-Readiness) calculation
- RAG (Retrieval-Augmented Generation) for semantic search
- Interactive Streamlit dashboards and visualizations

### Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Backend Framework** | FastAPI 0.109+ | High-performance async API framework |
| **Data Validation** | Pydantic v2 | Type-safe data models with validation |
| **Database** | Snowflake | Cloud data warehouse for analytics |
| **Caching** | Redis 7 | In-memory data store for performance |
| **Storage** | AWS S3 | Document and file storage |
| **Containerization** | Docker & Docker Compose | Application packaging and orchestration |
| **Testing** | Pytest | Comprehensive testing framework |
| **Language** | Python 3.12+ | Modern Python with type hints |

---

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (API Consumers: Web Apps, Mobile Apps, Internal Tools)         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Health     │  │  Industries  │  │  Companies   │          │
│  │   Router     │  │   Router     │  │   Router     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ Assessments  │  │    Scores    │                            │
│  │   Router     │  │   Router     │                            │
│  └──────────────┘  └──────────────┘                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────┐        │
│  │            Pydantic Models & Validation            │        │
│  └────────────────────────────────────────────────────┘        │
└────────┬────────────────────┬──────────────────┬───────────────┘
         │                    │                  │
         │                    │                  │
         ▼                    ▼                  ▼
┌──────────────────┐ ┌─────────────────┐ ┌────────────────┐
│  Redis Cache     │ │   Snowflake DB  │ │    AWS S3      │
│                  │ │                 │ │                │
│ • TTL-based      │ │ • Industries    │ │ • Documents    │
│ • Auto-invalidate│ │ • Companies     │ │ • Reports      │
│ • Performance    │ │ • Assessments   │ │ • Evidence     │
│                  │ │ • Scores        │ │                │
└──────────────────┘ └─────────────────┘ └────────────────┘
```

### Data Flow

1. **Request Flow**:
   - Client sends HTTP request to FastAPI endpoint
   - Pydantic models validate request data
   - Router checks Redis cache for existing data
   - If cache miss, query Snowflake database
   - Cache result in Redis with appropriate TTL
   - Return response to client

2. **Write Flow**:
   - Client sends write request (POST/PUT/PATCH/DELETE)
   - Pydantic validates incoming data
   - Write to Snowflake database
   - Invalidate relevant Redis cache entries
   - Return success response

3. **Health Check Flow**:
   - Health endpoint tests connectivity to all services
   - Returns aggregated health status
   - Used for monitoring and deployment validation

---

## Directory Structure

```
pe-org-air-platform/
├── app/                          # Main application directory
│   ├── config.py                 # Configuration management with Pydantic settings
│   ├── database/                 # Database schemas and migrations
│   │   ├── __init__.py
│   │   └── schema.sql            # Snowflake table definitions
│   ├── __init__.py
│   ├── logging.py                # Structured logging configuration
│   ├── main.py                   # FastAPI application entry point
│   ├── models/                   # Pydantic data models
│   │   ├── assessment.py         # Assessment models with validation
│   │   ├── company.py            # Company models with ticker validation
│   │   ├── dimension.py          # Dimension score models
│   │   ├── industry.py           # Industry models
│   │   └── __init__.py
│   ├── routers/                  # API route handlers
│   │   ├── assessments.py        # Assessment CRUD endpoints
│   │   ├── companies.py          # Company CRUD endpoints
│   │   ├── health.py             # Health check endpoint
│   │   ├── industries.py         # Industry CRUD endpoints
│   │   ├── __init__.py
│   │   └── scores.py             # Dimension score endpoints
│   ├── services/                 # External service integrations
│   │   ├── __init__.py
│   │   ├── redis_cache.py        # Redis caching service
│   │   ├── s3_storage.py         # AWS S3 storage service
│   │   └── snowflake.py          # Snowflake database service
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       └── pagination.py         # Pagination helper functions
├── docker/                       # Docker configuration
│   ├── compose.yaml              # Docker Compose orchestration
│   ├── Dockerfile                # Application container definition
│   └── README.Docker.md          # Docker-specific documentation
├── docs/                         # Documentation
│   └── CONFIGURATION.md          # Configuration guide
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── scripts/                      # Utility scripts
│   └── validate_config.py        # Configuration validation script
└── tests/                        # Test suite
    ├── conftest.py               # Pytest configuration and fixtures
    ├── __init__.py
    ├── test_api.py               # API endpoint tests
    ├── test_config.py            # Configuration tests
    └── test_models.py            # Pydantic model tests
```

**Key Components:**

- **app/main.py**: FastAPI application initialization and router registration
- **app/models/**: Pydantic models with field and model validators
- **app/routers/**: API endpoints organized by resource type
- **app/services/**: External service integrations (Snowflake, Redis, S3)
- **tests/**: Comprehensive test suite with 95%+ coverage
- **docker/**: Containerization configuration for consistent deployments

---

## Features

### Current Implementation (Case Study 1)

- ✅ RESTful API with 17+ endpoints
- ✅ Full CRUD operations for Industries, Companies, Assessments, and Dimension Scores
- ✅ Pydantic data validation with field and model validators
- ✅ Redis caching with TTL and automatic invalidation
- ✅ Snowflake integration with optimized queries and indexes
- ✅ Health check endpoint with dependency monitoring
- ✅ Pagination support for list endpoints
- ✅ Docker containerization
- ✅ Comprehensive error handling and structured logging

### Seven Dimensions of AI-Readiness

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Data Infrastructure (D1) | 0.25 | Quality, accessibility, and governance of data assets |
| AI Governance (D2) | 0.20 | Policies, ethics frameworks, compliance readiness |
| Technology Stack (D3) | 0.15 | Cloud infrastructure, ML tooling, API architecture |
| Talent & Skills (D4) | 0.15 | AI/ML talent density, retention, training programs |
| Leadership & Vision (D5) | 0.10 | Executive commitment, AI strategy, investment appetite |
| Use Case Portfolio (D6) | 0.10 | AI projects in production, pipeline, ROI tracking |
| Culture & Change (D7) | 0.05 | Innovation culture, change readiness, adoption rates |

---

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Snowflake account with database access
- AWS account with S3 bucket
- Redis instance (or use the Docker Compose provided one)
- Python 3.12+ (for local development)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pe-org-air-platform
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and fill in your credentials:
   ```bash
   # Snowflake Configuration
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_DATABASE=PE_ORG_AIR_DB
   SNOWFLAKE_SCHEMA=PE_ORG_AIR_SCHEMA
   SNOWFLAKE_WAREHOUSE=PE_ORG_AIR_WH

   # Redis Configuration
   REDIS_HOST=redis
   REDIS_PORT=6379
   REDIS_PASSWORD=
   REDIS_DB=0

   # AWS S3 Configuration
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your_bucket_name
   ```

3. **Initialize Snowflake database**

   Run the schema SQL in your Snowflake account:
   ```bash
   # Connect to Snowflake and run:
   # app/database/schema.sql
   ```

4. **Start the application**
   ```bash
   cd docker
   docker compose up --build
   ```

5. **Verify the application is running**
   ```bash
   curl http://localhost:8000/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2026-02-05T12:00:00Z",
     "version": "1.0.0",
     "dependencies": {
       "snowflake": "ok",
       "redis": "ok",
       "s3": "ok"
     }
   }
   ```

---

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Run specific test file
```bash
pytest tests/test_api.py -v
pytest tests/test_models.py -v
```

### Run tests in Docker
```bash
docker compose run --rm server pytest
```

---

## API Documentation

### Interactive Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Available Endpoints

#### Health Check
- `GET /health` - Check system health and dependencies

#### Industries
- `POST /api/v1/industries` - Create a new industry
- `GET /api/v1/industries` - List all industries (paginated)
- `GET /api/v1/industries/{id}` - Get industry by ID
- `PUT /api/v1/industries/{id}` - Update industry
- `DELETE /api/v1/industries/{id}` - Delete industry

#### Companies
- `POST /api/v1/companies` - Create a new company
- `GET /api/v1/companies` - List all companies (paginated)
- `GET /api/v1/companies/{id}` - Get company by ID
- `PUT /api/v1/companies/{id}` - Update company
- `DELETE /api/v1/companies/{id}` - Delete company

#### Assessments
- `POST /api/v1/assessments` - Create a new assessment
- `GET /api/v1/assessments` - List all assessments (paginated)
- `GET /api/v1/assessments/{id}` - Get assessment by ID
- `PATCH /api/v1/assessments/{id}` - Update assessment
- `PATCH /api/v1/assessments/{id}/status` - Update assessment status
- `POST /api/v1/assessments/{id}/scores` - Add dimension scores
- `GET /api/v1/assessments/{id}/scores` - Get dimension scores

#### Dimension Scores
- `PUT /api/v1/scores/{id}` - Update a specific dimension score

---

## Project Structure

```
pe-org-air-platform/
├── app
│   ├── config.py
│   ├── database
│   │   ├── __init__.py
│   │   └── schema.sql
│   ├── __init__.py
│   ├── logging.py
│   ├── main.py
│   ├── models
│   │   ├── assessment.py
│   │   ├── company.py
│   │   ├── dimension.py
│   │   ├── industry.py
│   │   └── __init__.py
│   ├── routers
│   │   ├── assessments.py
│   │   ├── companies.py
│   │   ├── health.py
│   │   ├── industries.py
│   │   ├── __init__.py
│   │   └── scores.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── redis_cache.py
│   │   ├── s3_storage.py
│   │   └── snowflake.py
│   └── utils
│       ├── __init__.py
│       └── pagination.py
├── docker
│   ├── compose.yaml
│   ├── Dockerfile
│   └── README.Docker.md
├── docs
│   └── CONFIGURATION.md
├── README.md
├── requirements.txt
├── scripts
│   └── validate_config.py
└── tests
    ├── conftest.py
    ├── __init__.py
    ├── test_api.py
    ├── test_config.py
    └── test_models.py
```

---

## Design Decisions

### Caching Strategy

We use Redis with a tiered TTL approach:

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Industries | 1 hour | Static reference data, rarely changes |
| Companies | 5 minutes | Frequently accessed, occasional updates |
| Assessments | 2 minutes | Active work items, may be updated frequently |

Cache invalidation occurs automatically on write operations (create/update/delete).

### Database Choice

**Snowflake** was chosen for:
- Native support for semi-structured data (JSON)
- Excellent analytics performance
- Separation of storage and compute
- Scalability for future AI/ML workloads

### Pagination Approach

- 1-indexed pagination (page numbers start at 1)
- Default page size: 50 items
- Maximum page size: 100 items
- Returns total count and total pages for client-side navigation

### Data Validation

We use Pydantic's two-tier validation:
1. **Field Validators** - Transform and validate individual fields (e.g., uppercase ticker symbols)
2. **Model Validators** - Cross-field validation (e.g., confidence_upper >= confidence_lower)

---

## Known Limitations

### Current Limitations

1. **Single-threaded Snowflake connections** - For production, consider connection pooling
2. **No authentication/authorization** - Security layer planned for Case Study 2
3. **Basic error responses** - Could be enhanced with more detailed error codes
4. **No rate limiting** - Should be added before public deployment
5. **Seed data uses hardcoded UUIDs** - Consider using database-generated IDs in production

### Future Enhancements (Upcoming Case Studies)

- **Case Study 2**: SEC filing ingestion and AI evidence extraction
- **Case Study 3**: Scoring engine with VR (Value-Readiness) calculation
- **Case Study 4**: RAG (Retrieval-Augmented Generation) for semantic search
- **Case Study 5**: Interactive dashboards and visualizations

---

## Development

### Local Development (without Docker)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Run tests**
   ```bash
   pytest -v
   ```

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose

### Logging

Structured logging is used throughout the application with `structlog`:
```python
log.info("event_name", key1=value1, key2=value2)
log.warning("warning_event", error=str(e))
log.debug("debug_info", details="...")
```

---

## Troubleshooting

### Common Issues

**Issue**: `snowflake_health_check_error`
- **Solution**: Verify Snowflake credentials in `.env` and ensure warehouse is running

**Issue**: `redis_connection_error`
- **Solution**: Check Redis is running with `docker compose ps` and verify REDIS_HOST/PORT

**Issue**: `ImportError: No module named 'app'`
- **Solution**: Ensure you're running from the project root directory

**Issue**: Ticker validation fails
- **Solution**: Ticker symbols are auto-converted to uppercase. Input can be lowercase.

### Debug Mode

Enable detailed logs by setting log level:
```python
# In app/logging.py, change level to DEBUG
log_level = "DEBUG"
```

---

## Contributing

This is an academic project for DAMG7245 - Big Data and Intelligent Analytics.

### Submission Requirements

- Individual work
- GitHub repository with complete code
- Comprehensive README (this file)
- All tests passing
- Docker builds successfully
- Screenshots in `docs/` folder

---

## License

Educational use only - Northeastern University DAMG7245 Spring 2026

---

## Contact

For questions or issues related to this case study:
- Course: DAMG7245 - Big Data and Intelligent Analytics
- Instructor: Sri Krishnamurthy - QuantUniversity
- Term: Spring 2026

---

## Acknowledgments

- **FastAPI** documentation and examples
- **Pydantic** validation framework
- **Snowflake** for cloud data warehousing
- QuantUniversity for the PE Org-AIR framework
