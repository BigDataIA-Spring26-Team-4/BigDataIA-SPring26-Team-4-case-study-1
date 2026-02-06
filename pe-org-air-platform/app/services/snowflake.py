"""
Snowflake database service for PE Org-AI-R Platform.

ORM models match EXACTLY the PDF schema (Section 5.1):
- Table names are PLURAL
- Field names match PDF exactly
- Data types match PDF specification
"""

import uuid
from datetime import datetime, date
from typing import Optional
from urllib.parse import quote_plus

import structlog
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Numeric,
    Date,
    DateTime,
    Integer,
    ForeignKey,
    func,
    Boolean,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from fastapi import HTTPException

from app.config import settings
from app.models.company import CompanyCreate, CompanyUpdate, IndustryCreate
from app.models.assessment import (
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentStatus,
    validate_status_transition,
)
from app.models.dimension import DimensionScoreCreate, DimensionScoreUpdate

log = structlog.get_logger(__name__)

# ============================================================================
# Engine & Session Setup
# ============================================================================

# Build connection string with URL-encoded credentials
connection_string = (
    f"snowflake://{quote_plus(settings.SNOWFLAKE_USER)}:"
    f"{quote_plus(settings.SNOWFLAKE_PASSWORD.get_secret_value())}@"
    f"{settings.SNOWFLAKE_ACCOUNT}/"
    f"{settings.SNOWFLAKE_DATABASE}/"
    f"{settings.SNOWFLAKE_SCHEMA}"
    f"?warehouse={settings.SNOWFLAKE_WAREHOUSE}"
)

if settings.SNOWFLAKE_ROLE:
    connection_string += f"&role={settings.SNOWFLAKE_ROLE}"

engine = create_engine(
    connection_string,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    log.debug("db_session_opened")
    try:
        yield db
    finally:
        db.close()
        log.debug("db_session_closed")


# ============================================================================
# ORM Models (Match PDF Section 5.1 EXACTLY)
# ============================================================================

class IndustryRow(Base):
    """Industries table - PDF Section 5.1, Line 2-8"""
    __tablename__ = "industries"  # PLURAL per PDF

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    sector = Column(String(100), nullable=False)
    h_r_base = Column(Numeric(5, 2), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())


class CompanyRow(Base):
    """Companies table - PDF Section 5.1, Line 10-21"""
    __tablename__ = "companies"  # PLURAL per PDF

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    ticker = Column(String(10), nullable=True)
    industry_id = Column(String(36), ForeignKey("industries.id"), nullable=False)
    position_factor = Column(Numeric(4, 3), nullable=False, default=0.0)  # DECIMAL(4,3) per PDF
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())


class AssessmentRow(Base):
    """Assessments table - PDF Section 5.1, Line 23-40"""
    __tablename__ = "assessments"  # PLURAL per PDF

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    assessment_type = Column(String(20), nullable=False)  # Not "type"!
    assessment_date = Column(Date, nullable=False)  # DATE not DATETIME per PDF
    status = Column(String(20), nullable=False, default="draft")
    primary_assessor = Column(String(255), nullable=True)  # Not "assessor_name"!
    secondary_assessor = Column(String(255), nullable=True)  # Not "assessor_email"!
    v_r_score = Column(Numeric(5, 2), nullable=True)  # DECIMAL(5,2) per PDF
    confidence_lower = Column(Numeric(5, 2), nullable=True)  # Not "lower_bound"!
    confidence_upper = Column(Numeric(5, 2), nullable=True)  # Not "upper_bound"!
    created_at = Column(DateTime, default=func.current_timestamp())


class DimensionScoreRow(Base):
    """Dimension_scores table - PDF Section 5.1, Line 42-58"""
    __tablename__ = "dimension_scores"  # PLURAL per PDF

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = Column(String(36), ForeignKey("assessments.id"), nullable=False)
    dimension = Column(String(30), nullable=False)
    score = Column(Numeric(5, 2), nullable=False)  # DECIMAL(5,2) per PDF
    weight = Column(Numeric(4, 3), nullable=False)  # DECIMAL(4,3) per PDF
    confidence = Column(Numeric(4, 3), nullable=False, default=0.8)  # DECIMAL(4,3) per PDF
    evidence_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=func.current_timestamp())


# ============================================================================
# Industry CRUD
# ============================================================================

def create_industry(db: Session, data: IndustryCreate) -> IndustryRow:
    """Create a new industry."""
    log.info("db_create_industry", name=data.name)
    row = IndustryRow(
        name=data.name,
        sector=data.sector,
        h_r_base=float(data.h_r_base),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_industries(db: Session) -> list[IndustryRow]:
    """List all industries."""
    log.debug("db_list_industries")
    return db.query(IndustryRow).all()


def get_industry(db: Session, industry_id: str) -> IndustryRow:
    """Get industry by ID."""
    row = db.query(IndustryRow).filter(IndustryRow.id == industry_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Industry not found")
    return row


# ============================================================================
# Company CRUD
# ============================================================================

def create_company(db: Session, data: CompanyCreate) -> CompanyRow:
    """Create a new company."""
    log.info("db_create_company", name=data.name)
    row = CompanyRow(
        name=data.name,
        ticker=data.ticker,
        industry_id=str(data.industry_id),
        position_factor=float(data.position_factor),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    log.info("db_company_created", company_id=row.id)
    return row


def list_companies(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    industry_id: Optional[str] = None
) -> list[CompanyRow]:
    """List companies with pagination and optional filtering."""
    log.debug("db_list_companies", skip=skip, limit=limit, industry_id=industry_id)
    
    query = db.query(CompanyRow).filter(CompanyRow.is_deleted == False)
    
    if industry_id:
        query = query.filter(CompanyRow.industry_id == industry_id)
    
    return query.offset(skip).limit(limit).all()


def count_companies(db: Session, industry_id: Optional[str] = None) -> int:
    """Count total companies (for pagination)."""
    query = db.query(CompanyRow).filter(CompanyRow.is_deleted == False)
    
    if industry_id:
        query = query.filter(CompanyRow.industry_id == industry_id)
    
    return query.count()


def get_company(db: Session, company_id: str) -> CompanyRow:
    """Get a company by ID."""
    log.debug("db_get_company", company_id=company_id)
    row = (
        db.query(CompanyRow)
        .filter(CompanyRow.id == company_id, CompanyRow.is_deleted == False)
        .first()
    )
    if not row:
        log.warning("company_not_found", company_id=company_id)
        raise HTTPException(status_code=404, detail="Company not found")
    return row


def update_company(db: Session, company_id: str, data: CompanyUpdate) -> CompanyRow:
    """Update a company."""
    log.info("db_update_company", company_id=company_id)
    row = get_company(db, company_id)
    
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if field == "industry_id" and value is not None:
            value = str(value)
        elif field == "position_factor" and value is not None:
            value = float(value)
        setattr(row, field, value)
    
    row.updated_at = datetime.now()
    db.commit()
    db.refresh(row)
    return row


def delete_company(db: Session, company_id: str) -> None:
    """Soft delete a company."""
    log.info("db_delete_company", company_id=company_id)
    row = get_company(db, company_id)
    row.is_deleted = True
    db.commit()


# ============================================================================
# Assessment CRUD
# ============================================================================

def create_assessment(db: Session, data: AssessmentCreate) -> AssessmentRow:
    """Create a new assessment."""
    log.info(
        "db_create_assessment",
        company_id=str(data.company_id),
        type=data.assessment_type.value
    )
    
    # Convert datetime to date if needed
    assessment_date = data.assessment_date
    if isinstance(assessment_date, datetime):
        assessment_date = assessment_date.date()
    
    row = AssessmentRow(
        company_id=str(data.company_id),
        assessment_type=data.assessment_type.value,
        assessment_date=assessment_date,
        status=AssessmentStatus.DRAFT.value,
        primary_assessor=data.primary_assessor,
        secondary_assessor=data.secondary_assessor,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    log.info("db_assessment_created", assessment_id=row.id)
    return row


def list_assessments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[str] = None
) -> list[AssessmentRow]:
    """List assessments with optional filtering."""
    log.debug("db_list_assessments", skip=skip, limit=limit, company_id=company_id)
    
    query = db.query(AssessmentRow)
    if company_id:
        query = query.filter(AssessmentRow.company_id == company_id)
    
    return query.offset(skip).limit(limit).all()


def count_assessments(db: Session, company_id: Optional[str] = None) -> int:
    """Count total assessments (for pagination)."""
    query = db.query(AssessmentRow)
    if company_id:
        query = query.filter(AssessmentRow.company_id == company_id)
    return query.count()


def get_assessment(db: Session, assessment_id: str) -> AssessmentRow:
    """Get an assessment by ID."""
    log.debug("db_get_assessment", assessment_id=assessment_id)
    row = db.query(AssessmentRow).filter(AssessmentRow.id == assessment_id).first()
    if not row:
        log.warning("assessment_not_found", assessment_id=assessment_id)
        raise HTTPException(status_code=404, detail="Assessment not found")
    return row


def update_assessment(
    db: Session,
    assessment_id: str,
    data: AssessmentUpdate
) -> AssessmentRow:
    """Update an assessment."""
    log.info("db_update_assessment", assessment_id=assessment_id)
    row = get_assessment(db, assessment_id)
    
    updates = data.model_dump(exclude_unset=True)
    
    # Validate status transition if status is being updated
    if "status" in updates and updates["status"] is not None:
        current_status = AssessmentStatus(row.status)
        new_status = updates["status"]
        
        if not validate_status_transition(current_status, new_status):
            log.warning(
                "invalid_status_transition",
                assessment_id=assessment_id,
                current=current_status.value,
                requested=new_status.value,
            )
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status transition from '{current_status.value}' to '{new_status.value}'"
            )
        updates["status"] = new_status.value
    
    # Convert enums to values
    if "assessment_type" in updates and updates["assessment_type"] is not None:
        updates["assessment_type"] = updates["assessment_type"].value
    
    if "company_id" in updates and updates["company_id"] is not None:
        updates["company_id"] = str(updates["company_id"])
    
    # Convert datetime to date if needed
    if "assessment_date" in updates and updates["assessment_date"] is not None:
        if isinstance(updates["assessment_date"], datetime):
            updates["assessment_date"] = updates["assessment_date"].date()
    
    # Convert numeric fields
    for field in ["v_r_score", "confidence_lower", "confidence_upper"]:
        if field in updates and updates[field] is not None:
            updates[field] = float(updates[field])
    
    for field, value in updates.items():
        setattr(row, field, value)
    
    db.commit()
    db.refresh(row)
    return row


# ============================================================================
# Dimension Score CRUD
# ============================================================================

def add_scores(
    db: Session,
    assessment_id: str,
    scores: list[DimensionScoreCreate]
) -> list[DimensionScoreRow]:
    """Add dimension scores to an assessment."""
    log.info("db_add_scores", assessment_id=assessment_id, count=len(scores))
    
    # Verify assessment exists
    get_assessment(db, assessment_id)
    
    rows = []
    for score in scores:
        row = DimensionScoreRow(
            assessment_id=assessment_id,
            dimension=score.dimension.value,
            score=float(score.score),
            weight=float(score.weight),
            confidence=float(score.confidence),
            evidence_count=score.evidence_count,
        )
        db.add(row)
        rows.append(row)
    
    db.commit()
    for r in rows:
        db.refresh(r)
    
    return rows


def get_scores(db: Session, assessment_id: str) -> list[DimensionScoreRow]:
    """Get all dimension scores for an assessment."""
    log.debug("db_get_scores", assessment_id=assessment_id)
    
    # Verify assessment exists
    get_assessment(db, assessment_id)
    
    return (
        db.query(DimensionScoreRow)
        .filter(DimensionScoreRow.assessment_id == assessment_id)
        .all()
    )


def update_score(
    db: Session,
    score_id: str,
    data: DimensionScoreUpdate
) -> DimensionScoreRow:
    """Update a single dimension score."""
    log.info("db_update_score", score_id=score_id)
    
    row = db.query(DimensionScoreRow).filter(DimensionScoreRow.id == score_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Dimension score not found")
    
    updates = data.model_dump(exclude_unset=True)
    
    # Convert numeric fields
    for field in ["score", "weight", "confidence"]:
        if field in updates and updates[field] is not None:
            updates[field] = float(updates[field])
    
    for field, value in updates.items():
        setattr(row, field, value)
    
    db.commit()
    db.refresh(row)
    return row
