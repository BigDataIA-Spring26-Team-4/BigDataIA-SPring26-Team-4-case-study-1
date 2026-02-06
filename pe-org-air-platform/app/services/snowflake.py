import uuid
from datetime import datetime, date

import structlog
from sqlalchemy import (
    create_engine, Column, String, Float, Date, DateTime, Integer,
    ForeignKey, func,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from fastapi import HTTPException

from app.config import get_settings
from app.models.company import CompanyCreate, CompanyUpdate
from app.models.assessment import AssessmentCreate, AssessmentUpdate, VALID_TRANSITIONS, AssessmentStatus
from app.models.dimension import DimensionScoreCreate, DimensionScoreUpdate
from app.models.industry import IndustryCreate, IndustryUpdate

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Engine & session
# ---------------------------------------------------------------------------

settings = get_settings()
engine = create_engine(settings.snowflake_url)
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


async def check_snowflake() -> dict:
    """Check Snowflake database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(func.current_timestamp())
        log.debug("snowflake_health_check_ok")
        return {"status": "ok", "error": None}
    except Exception as e:
        log.error("snowflake_health_check_error", error=str(e))
        return {"status": "error", "error": str(e)}


# ---------------------------------------------------------------------------
# ORM models
# ---------------------------------------------------------------------------

class IndustryRow(Base):
    __tablename__ = "industry"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    sector = Column(String(255), nullable=False)
    h_r_base = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())


class CompanyRow(Base):
    __tablename__ = "company"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    ticker = Column(String(10), nullable=True)
    industry_id = Column(String(36), ForeignKey("industry.id"), nullable=False)
    position_factor = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())


class AssessmentRow(Base):
    __tablename__ = "assessment"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("company.id"), nullable=False)
    type = Column(String(50), nullable=False)
    assessment_date = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    vr_score = Column(Float, nullable=True)
    confidence_lower = Column(Float, nullable=True)
    confidence_upper = Column(Float, nullable=True)
    primary_assessor = Column(String(255), nullable=True)
    secondary_assessor = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())


class DimensionScoreRow(Base):
    __tablename__ = "dimension_score"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = Column(String(36), ForeignKey("assessment.id"), nullable=False)
    dimension = Column(String(50), nullable=False)
    score = Column(Float, nullable=False)
    weight = Column(Float, nullable=True)
    confidence = Column(Float, nullable=False, default=0.8)
    evidence_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())


# ---------------------------------------------------------------------------
# Pagination Helper
# ---------------------------------------------------------------------------

def paginate_query(query, page: int, page_size: int) -> tuple[list, int]:
    """
    Apply pagination to a SQLAlchemy query and return items + total count.

    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        tuple: (items list, total_count)
    """
    total_count = query.count()
    skip = (page - 1) * page_size
    items = query.offset(skip).limit(page_size).all()
    return items, total_count


# ---------------------------------------------------------------------------
# Industry CRUD
# ---------------------------------------------------------------------------

def create_industry(db: Session, data: IndustryCreate) -> IndustryRow:
    log.info("db_create_industry", name=data.name)
    row = IndustryRow(
        name=data.name,
        sector=data.sector,
        h_r_base=data.h_r_base,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    log.info("db_industry_created", industry_id=row.id)
    return row


def list_industries(db: Session, page: int = 1, page_size: int = 50) -> tuple[list[IndustryRow], int]:
    log.debug("db_list_industries", page=page, page_size=page_size)
    query = db.query(IndustryRow)
    return paginate_query(query, page, page_size)


def get_industry(db: Session, industry_id: str) -> IndustryRow:
    log.debug("db_get_industry", industry_id=industry_id)
    row = db.query(IndustryRow).filter(IndustryRow.id == industry_id).first()
    if not row:
        log.warning("industry_not_found", industry_id=industry_id)
        raise HTTPException(status_code=404, detail="Industry not found")
    return row


def update_industry(db: Session, industry_id: str, data: IndustryUpdate) -> IndustryRow:
    log.info("db_update_industry", industry_id=industry_id)
    row = get_industry(db, industry_id)
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row


def delete_industry(db: Session, industry_id: str) -> None:
    log.info("db_delete_industry", industry_id=industry_id)
    row = get_industry(db, industry_id)
    db.delete(row)
    db.commit()


# ---------------------------------------------------------------------------
# Company CRUD
# ---------------------------------------------------------------------------

def create_company(db: Session, data: CompanyCreate) -> CompanyRow:
    log.info("db_create_company", name=data.name)
    row = CompanyRow(
        name=data.name,
        ticker=data.ticker,
        industry_id=str(data.industry_id),
        position_factor=data.position_factor,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    log.info("db_company_created", company_id=row.id)
    return row


def list_companies(db: Session, page: int = 1, page_size: int = 50) -> tuple[list[CompanyRow], int]:
    log.debug("db_list_companies", page=page, page_size=page_size)
    query = db.query(CompanyRow)
    return paginate_query(query, page, page_size)


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
        confidence_lower=data.confidence_lower,
        confidence_upper=data.confidence_upper,
        primary_assessor=data.primary_assessor,
        secondary_assessor=data.secondary_assessor,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    log.info("db_assessment_created", assessment_id=row.id)
    return row


def list_assessments(db: Session, page: int = 1, page_size: int = 50) -> tuple[list[AssessmentRow], int]:
    log.debug("db_list_assessments", page=page, page_size=page_size)
    query = db.query(AssessmentRow)
    return paginate_query(query, page, page_size)


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


def update_score(db: Session, score_id: str, data: DimensionScoreUpdate) -> DimensionScoreRow:
    log.info("db_update_score", score_id=score_id)
    row = db.query(DimensionScoreRow).filter(DimensionScoreRow.id == score_id).first()
    if not row:
        log.warning("score_not_found", score_id=score_id)
        raise HTTPException(status_code=404, detail="Score not found")

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row
