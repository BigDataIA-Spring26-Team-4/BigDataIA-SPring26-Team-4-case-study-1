from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response

from app.logging import setup_logging
from app.routers import health, companies, assessments

setup_logging()
log = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("application_startup")
    yield
    log.info("application_shutdown")


app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(companies.router)
app.include_router(assessments.router)


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
