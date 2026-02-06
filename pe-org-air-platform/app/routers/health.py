import structlog
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
from datetime import datetime, timezone

from app.services.snowflake import check_snowflake
from app.services.redis_cache import check_redis
from app.services.s3_storage import check_s3

log = structlog.get_logger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    dependencies: Dict[str, str]


@router.get("/health", response_model=HealthResponse)
async def show_health() -> HealthResponse:
    log.debug("health_check")

    # Check all dependencies
    snowflake_health = await check_snowflake()
    redis_health = await check_redis()
    s3_health = await check_s3()

    dependencies = {
        "snowflake": snowflake_health,
        "redis": redis_health,
        "s3": s3_health
    }

    # Overall status
    all_ok = all(dep["status"] == "ok" for dep in dependencies.values())
    overall_status = "healthy" if all_ok else "degraded"

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc),
        version="1.0.0",
        dependencies={k: v["status"] for k, v in dependencies.items()}
    )
