# PE Org-AIR Platform - Platform Foundation

## Project Overview

The **PE Org-AIR (Organizational AI-Readiness) Platform** is a data-driven system for private equity firms to assess the AI-readiness of portfolio companies and acquisition targets. The platform provides systematic evaluation across seven dimensions of AI-readiness, helping firms make informed decisions about investments and value creation opportunities.

### Technologies Used

- **FastAPI** - Modern, fast web framework for building APIs
- **Pydantic v2** - Data validation and settings management using Python type annotations
- **Docker & Docker Compose** - Containerization and orchestration
- **Snowflake** - Cloud data warehouse for analytics
- **Redis** - In-memory caching layer
- **AWS S3** - Document storage
- **SQLAlchemy** - ORM for database operations
- **Pytest** - Testing framework

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
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   ├── logging.py                 # Structured logging setup
│   ├── models/                    # Pydantic data models
│   │   ├── assessment.py          # Assessment models & enums
│   │   ├── company.py             # Company models
│   │   ├── dimension.py           # Dimension score models
│   │   └── industry.py            # Industry models
│   ├── routers/                   # API endpoint routers
│   │   ├── assessments.py
│   │   ├── companies.py
│   │   ├── health.py
│   │   ├── industries.py
│   │   └── scores.py
│   ├── services/                  # Business logic & integrations
│   │   ├── redis_cache.py         # Redis caching layer
│   │   ├── s3_storage.py          # S3 document storage
│   │   └── snowflake.py           # Snowflake database ORM
│   ├── utils/                     # Utility functions
│   │   └── pagination.py          # Pagination helpers
│   └── database/
│       └── schema.sql             # Snowflake DDL & seed data
├── tests/
│   ├── conftest.py                # Pytest fixtures
│   ├── test_api.py                # API endpoint tests
│   └── test_models.py             # Model validation tests
├── docker/
│   ├── Dockerfile
│   └── compose.yaml
├── requirements.txt
├── .env.example
└── README.md
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
