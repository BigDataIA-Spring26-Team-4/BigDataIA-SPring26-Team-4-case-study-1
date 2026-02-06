from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from pydantic import ValidationError

from app.config import get_settings
from app.logging import setup_logging
from app.routers import health, companies, assessments, scores, industries

# Initialize logging first
setup_logging()
log = structlog.get_logger(__name__)

# Validate configuration at startup
try:
    settings = get_settings()
    log.info(
        "configuration_loaded",
        app_name=settings.APP_NAME,
        app_version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        debug=settings.DEBUG,
    )
except ValidationError as e:
    log.error("configuration_validation_failed", errors=e.errors())
    raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info(
        "application_startup",
        environment=settings.APP_ENV,
        snowflake_database=settings.SNOWFLAKE_DATABASE,
        redis_host=settings.REDIS_HOST,
        s3_bucket=settings.S3_BUCKET_NAME,
    )
    yield
    log.info("application_shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(industries.router)
app.include_router(companies.router)
app.include_router(assessments.router)
app.include_router(scores.router)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    log.info("request_started", method=request.method, path=request.url.path)
    response: Response = await call_next(request)
    log.info(
        "request_finished",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )
    return response
