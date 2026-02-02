import os
import uuid
from datetime import datetime, date

import structlog
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import (
    create_engine, Column, String, Float, Date, DateTime, Integer,
    ForeignKey, func,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from fastapi import HTTPException

from app.models.company import CompanyCreate, CompanyUpdate
from app.models.assessment import AssessmentCreate, AssessmentUpdate, VALID_TRANSITIONS, AssessmentStatus
from app.models.dimension import DimensionScoreCreate, DimensionScoreUpdate

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Engine & session
# ---------------------------------------------------------------------------

SNOWFLAKE_URL = os.getenv(
    "SNOWFLAKE_URL",
    "snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}".format(
        user=os.getenv("SNOWFLAKE_USER", ""),
        password=os.getenv("SNOWFLAKE_PASSWORD", ""),
        account=os.getenv("SNOWFLAKE_ACCOUNT", ""),
        database=os.getenv("SNOWFLAKE_DATABASE", ""),
        schema=os.getenv("SNOWFLAKE_SCHEMA", ""),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", ""),
    ),
)

engine = create_engine(SNOWFLAKE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    log.debug("db_session_opened")
    try:
        yield db
    finally:
        db.close()
        log.debug("db_session_closed")


# ---------------------------------------------------------------------------
# ORM models
# ---------------------------------------------------------------------------

class CompanyRow(Base):
    __tablename__ = "company"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    ticker = Column(String(10), nullable=True)
    industry_id = Column(String(36), ForeignKey("industry.id"), nullable=False)
    position = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())


class AssessmentRow(Base):
    __tablename__ = "assessment"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("company.id"), nullable=False)
    type = Column(String(50), nullable=False)
    assessment_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    vr_score = Column(Float, nullable=True)
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)
    assessor_name = Column(String(255), nullable=True)
    assessor_email = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())


class DimensionScoreRow(Base):
    __tablename__ = "dimension_score"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = Column(String(36), ForeignKey("assessment.id"), nullable=False)
    dimension = Column(String(50), nullable=False)
    score = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    evidence_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())


# ---------------------------------------------------------------------------
# Company CRUD
# ---------------------------------------------------------------------------

def create_company(db: Session, data: CompanyCreate) -> CompanyRow:
    log.info("db_create_company", name=data.name)
    row = CompanyRow(
        name=data.name,
        ticker=data.ticker,
        industry_id=str(data.industry_id),
        position=data.position,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    log.info("db_company_created", company_id=row.id)
    return row


def list_companies(db: Session) -> list[CompanyRow]:
    log.debug("db_list_companies")
    return db.query(CompanyRow).all()


def get_company(db: Session, company_id: str) -> CompanyRow:
    log.debug("db_get_company", company_id=company_id)
    row = db.query(CompanyRow).filter(CompanyRow.id == company_id).first()
    if not row:
        log.warning("company_not_found", company_id=company_id)
        raise HTTPException(status_code=404, detail="Company not found")
    return row


def update_company(db: Session, company_id: str, data: CompanyUpdate) -> CompanyRow:
    log.info("db_update_company", company_id=company_id)
    row = get_company(db, company_id)
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if field == "industry_id" and value is not None:
            value = str(value)
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row


def delete_company(db: Session, company_id: str) -> None:
    log.info("db_delete_company", company_id=company_id)
    row = get_company(db, company_id)
    db.delete(row)
    db.commit()


# ---------------------------------------------------------------------------
# Assessment CRUD
# ---------------------------------------------------------------------------

def create_assessment(db: Session, data: AssessmentCreate) -> AssessmentRow:
    log.info("db_create_assessment", company_id=str(data.company_id), type=data.type.value)
    row = AssessmentRow(
        company_id=str(data.company_id),
        type=data.type.value,
        assessment_date=data.assessment_date,
        status=data.status.value,
        vr_score=data.vr_score,
        lower_bound=data.lower_bound,
        upper_bound=data.upper_bound,
        assessor_name=data.assessor_name,
        assessor_email=data.assessor_email,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    log.info("db_assessment_created", assessment_id=row.id)
    return row


def list_assessments(db: Session) -> list[AssessmentRow]:
    log.debug("db_list_assessments")
    return db.query(AssessmentRow).all()


def get_assessment(db: Session, assessment_id: str) -> AssessmentRow:
    log.debug("db_get_assessment", assessment_id=assessment_id)
    row = db.query(AssessmentRow).filter(AssessmentRow.id == assessment_id).first()
    if not row:
        log.warning("assessment_not_found", assessment_id=assessment_id)
        raise HTTPException(status_code=404, detail="Assessment not found")
    return row


def update_assessment(db: Session, assessment_id: str, data: AssessmentUpdate) -> AssessmentRow:
    log.info("db_update_assessment", assessment_id=assessment_id)
    row = get_assessment(db, assessment_id)
    updates = data.model_dump(exclude_unset=True)

    # Validate status transition
    if "status" in updates and updates["status"] is not None:
        current = AssessmentStatus(row.status)
        requested = updates["status"]
        if requested not in VALID_TRANSITIONS[current]:
            log.warning(
                "invalid_status_transition",
                assessment_id=assessment_id,
                current=current.value,
                requested=requested.value,
            )
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status transition from '{current.value}' to '{requested.value}'",
            )
        updates["status"] = requested.value

    if "type" in updates and updates["type"] is not None:
        updates["type"] = updates["type"].value

    if "company_id" in updates and updates["company_id"] is not None:
        updates["company_id"] = str(updates["company_id"])

    for field, value in updates.items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row


# ---------------------------------------------------------------------------
# Dimension score CRUD
# ---------------------------------------------------------------------------

def add_scores(db: Session, assessment_id: str, scores: list[DimensionScoreCreate]) -> list[DimensionScoreRow]:
    log.info("db_add_scores", assessment_id=assessment_id, count=len(scores))
    # Verify assessment exists
    get_assessment(db, assessment_id)

    rows = []
    for s in scores:
        row = DimensionScoreRow(
            assessment_id=assessment_id,
            dimension=s.dimension.value,
            score=s.score,
            weight=s.weight,
            confidence=s.confidence,
            evidence_count=s.evidence_count,
        )
        db.add(row)
        rows.append(row)
    db.commit()
    for r in rows:
        db.refresh(r)
    return rows


def get_scores(db: Session, assessment_id: str) -> list[DimensionScoreRow]:
    log.debug("db_get_scores", assessment_id=assessment_id)
    get_assessment(db, assessment_id)
    return db.query(DimensionScoreRow).filter(DimensionScoreRow.assessment_id == assessment_id).all()


def update_scores(db: Session, assessment_id: str, scores: list[DimensionScoreUpdate]) -> list[DimensionScoreRow]:
    log.info("db_update_scores", assessment_id=assessment_id, count=len(scores))
    existing = get_scores(db, assessment_id)
    if len(scores) != len(existing):
        log.warning(
            "score_count_mismatch",
            assessment_id=assessment_id,
            expected=len(existing),
            got=len(scores),
        )
        raise HTTPException(
            status_code=400,
            detail=f"Expected {len(existing)} scores, got {len(scores)}",
        )

    for row, update in zip(existing, scores):
        updates = update.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(row, field, value)
    db.commit()
    for r in existing:
        db.refresh(r)
    return existing
