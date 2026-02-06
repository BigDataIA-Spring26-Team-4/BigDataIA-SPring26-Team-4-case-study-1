import math
import structlog
from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.assessment import AssessmentCreate, AssessmentUpdate, AssessmentResponse, AssessmentStatus
from app.models.dimension import DimensionScoreCreate, DimensionScoreResponse
from app.services import snowflake
from app.services.snowflake import get_db
from app.services.redis_cache import cached, invalidate
from app.utils.pagination import PaginatedResponse

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v1/assessments", tags=["assessments"])

CACHE_PREFIX = "assessments:"


@router.post("", response_model=AssessmentResponse)
def create_assessment(assessment: AssessmentCreate, db: Session = Depends(get_db)):
    log.info("creating_assessment", company_id=str(assessment.company_id), type=assessment.type.value)
    result = snowflake.create_assessment(db, assessment)
    invalidate(CACHE_PREFIX)
    log.info("assessment_created", assessment_id=result.id)
    return result


@router.get("", response_model=PaginatedResponse[AssessmentResponse])
@cached(prefix=CACHE_PREFIX, exclude=["db"])
def list_assessments(page: int = 1, page_size: int = 50, db: Session = Depends(get_db)):
    log.info("listing_assessments", page=page, page_size=page_size)

    # Validate and cap page_size
    if page_size > 100:
        page_size = 100
    if page < 1:
        page = 1

    items, total_count = snowflake.list_assessments(db, page, page_size)
    total_pages = math.ceil(total_count / page_size) if page_size > 0 else 0

    return PaginatedResponse(
        items=items,
        page=page,
        page_size=page_size,
        total_count=total_count,
        total_pages=total_pages
    )


@router.get("/{assessment_id}", response_model=AssessmentResponse)
@cached(prefix=CACHE_PREFIX, exclude=["db"], ttl=120)  # 2 minutes
def get_assessment(assessment_id: UUID, db: Session = Depends(get_db)):
    log.info("getting_assessment", assessment_id=str(assessment_id))
    return snowflake.get_assessment(db, str(assessment_id))


@router.patch("/{assessment_id}", response_model=AssessmentResponse)
def update_assessment(assessment_id: UUID, assessment: AssessmentUpdate, db: Session = Depends(get_db)):
    log.info("updating_assessment", assessment_id=str(assessment_id))
    result = snowflake.update_assessment(db, str(assessment_id), assessment)
    invalidate(CACHE_PREFIX)
    log.info("assessment_updated", assessment_id=str(assessment_id))
    return result


@router.patch("/{assessment_id}/status", response_model=AssessmentResponse)
def update_assessment_status(assessment_id: UUID, status: AssessmentStatus, db: Session = Depends(get_db)):
    log.info("updating_assessment_status", assessment_id=str(assessment_id), status=status.value)
    update_data = AssessmentUpdate(status=status)
    result = snowflake.update_assessment(db, str(assessment_id), update_data)
    invalidate(CACHE_PREFIX)
    log.info("assessment_status_updated", assessment_id=str(assessment_id))
    return result


@router.post("/{assessment_id}/scores", response_model=list[DimensionScoreResponse])
def add_scores(assessment_id: UUID, scores: list[DimensionScoreCreate], db: Session = Depends(get_db)):
    log.info("adding_scores", assessment_id=str(assessment_id), count=len(scores))
    result = snowflake.add_scores(db, str(assessment_id), scores)
    invalidate(CACHE_PREFIX)
    log.info("scores_added", assessment_id=str(assessment_id), count=len(scores))
    return result


@router.get("/{assessment_id}/scores", response_model=list[DimensionScoreResponse])
@cached(prefix=CACHE_PREFIX, exclude=["db"])
def get_scores(assessment_id: UUID, db: Session = Depends(get_db)):
    log.info("getting_scores", assessment_id=str(assessment_id))
    return snowflake.get_scores(db, str(assessment_id))
