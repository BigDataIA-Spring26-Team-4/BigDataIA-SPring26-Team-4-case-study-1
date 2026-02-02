import structlog
from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.assessment import AssessmentCreate, AssessmentUpdate, AssessmentResponse
from app.models.dimension import DimensionScoreCreate, DimensionScoreUpdate, DimensionScoreResponse
from app.services import snowflake
from app.services.snowflake import get_db
from app.services.redis_cache import cached, invalidate

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


@router.get("", response_model=list[AssessmentResponse])
@cached(prefix=CACHE_PREFIX)
def list_assessments(db: Session = Depends(get_db)):
    log.info("listing_assessments")
    return snowflake.list_assessments(db)


@router.get("/{assessment_id}", response_model=AssessmentResponse)
@cached(prefix=CACHE_PREFIX)
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


@router.post("/{assessment_id}/scores", response_model=list[DimensionScoreResponse])
def add_scores(assessment_id: UUID, scores: list[DimensionScoreCreate], db: Session = Depends(get_db)):
    log.info("adding_scores", assessment_id=str(assessment_id), count=len(scores))
    result = snowflake.add_scores(db, str(assessment_id), scores)
    invalidate(CACHE_PREFIX)
    log.info("scores_added", assessment_id=str(assessment_id), count=len(scores))
    return result


@router.get("/{assessment_id}/scores", response_model=list[DimensionScoreResponse])
@cached(prefix=CACHE_PREFIX)
def get_scores(assessment_id: UUID, db: Session = Depends(get_db)):
    log.info("getting_scores", assessment_id=str(assessment_id))
    return snowflake.get_scores(db, str(assessment_id))


@router.put("/{assessment_id}/scores", response_model=list[DimensionScoreResponse])
def update_scores(assessment_id: UUID, scores: list[DimensionScoreUpdate], db: Session = Depends(get_db)):
    log.info("updating_scores", assessment_id=str(assessment_id), count=len(scores))
    result = snowflake.update_scores(db, str(assessment_id), scores)
    invalidate(CACHE_PREFIX)
    log.info("scores_updated", assessment_id=str(assessment_id))
    return result
