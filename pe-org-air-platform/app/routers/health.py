import structlog
from fastapi import APIRouter

log = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/health")
def show_health() -> dict:
    log.debug("health_check")
    return {"status": "ok"}
