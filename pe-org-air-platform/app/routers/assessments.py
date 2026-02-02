from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.assessment import AssessmentCreate, AssessmentUpdate, AssessmentResponse
from app.models.dimension import DimensionScoreCreate, DimensionScoreUpdate, DimensionScoreResponse
from app.services import snowflake
from app.services.snowflake import get_db

router = APIRouter(prefix="/api/v1/assessments", tags=["assessments"])


@router.post("", response_model=AssessmentResponse)
def create_assessment(assessment: AssessmentCreate, db: Session = Depends(get_db)):
    return snowflake.create_assessment(db, assessment)


@router.get("", response_model=list[AssessmentResponse])
def list_assessments(db: Session = Depends(get_db)):
    return snowflake.list_assessments(db)


@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(assessment_id: UUID, db: Session = Depends(get_db)):
    return snowflake.get_assessment(db, str(assessment_id))


@router.patch("/{assessment_id}", response_model=AssessmentResponse)
def update_assessment(assessment_id: UUID, assessment: AssessmentUpdate, db: Session = Depends(get_db)):
    return snowflake.update_assessment(db, str(assessment_id), assessment)


@router.post("/{assessment_id}/scores", response_model=list[DimensionScoreResponse])
def add_scores(assessment_id: UUID, scores: list[DimensionScoreCreate], db: Session = Depends(get_db)):
    return snowflake.add_scores(db, str(assessment_id), scores)


@router.get("/{assessment_id}/scores", response_model=list[DimensionScoreResponse])
def get_scores(assessment_id: UUID, db: Session = Depends(get_db)):
    return snowflake.get_scores(db, str(assessment_id))


@router.put("/{assessment_id}/scores", response_model=list[DimensionScoreResponse])
def update_scores(assessment_id: UUID, scores: list[DimensionScoreUpdate], db: Session = Depends(get_db)):
    return snowflake.update_scores(db, str(assessment_id), scores)
