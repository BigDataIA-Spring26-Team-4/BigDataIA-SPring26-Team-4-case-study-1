import structlog
from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.dimension import DimensionScoreUpdate, DimensionScoreResponse
from app.services import snowflake
from app.services.snowflake import get_db
from app.services.redis_cache import invalidate

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v1/scores", tags=["scores"])

CACHE_PREFIX = "assessments:"


@router.put("/{id}", response_model=DimensionScoreResponse)
def update_score(id: UUID, score: DimensionScoreUpdate, db: Session = Depends(get_db)):
    log.info("updating_score", score_id=str(id))
    result = snowflake.update_score(db, str(id), score)
    invalidate(CACHE_PREFIX)
    log.info("score_updated", score_id=str(id))
    return result
