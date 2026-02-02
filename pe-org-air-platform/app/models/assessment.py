from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from enum import Enum


class AssessmentType(str, Enum):
    INITIAL = "initial"
    ANNUAL = "annual"
    QUARTERLY = "quarterly"
    AD_HOC = "ad_hoc"


class AssessmentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"
    CANCELLED = "cancelled"


# Valid state transitions: status -> allowed next statuses
VALID_TRANSITIONS: dict[AssessmentStatus, list[AssessmentStatus]] = {
    AssessmentStatus.PENDING: [AssessmentStatus.IN_PROGRESS, AssessmentStatus.CANCELLED],
    AssessmentStatus.IN_PROGRESS: [AssessmentStatus.COMPLETED, AssessmentStatus.CANCELLED],
    AssessmentStatus.COMPLETED: [AssessmentStatus.REVIEWED],
    AssessmentStatus.REVIEWED: [],
    AssessmentStatus.CANCELLED: [],
}


class AssessmentBase(BaseModel):
    company_id: UUID
    type: AssessmentType
    assessment_date: date
    status: AssessmentStatus = AssessmentStatus.PENDING
    vr_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    lower_bound: Optional[float] = Field(None, ge=0.0, le=100.0)
    upper_bound: Optional[float] = Field(None, ge=0.0, le=100.0)
    assessor_name: Optional[str] = Field(None, max_length=255)
    assessor_email: Optional[str] = Field(None, max_length=255)


class AssessmentCreate(AssessmentBase):
    pass


class AssessmentUpdate(BaseModel):
    type: Optional[AssessmentType] = None
    assessment_date: Optional[date] = None
    status: Optional[AssessmentStatus] = None
    vr_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    lower_bound: Optional[float] = Field(None, ge=0.0, le=100.0)
    upper_bound: Optional[float] = Field(None, ge=0.0, le=100.0)
    assessor_name: Optional[str] = Field(None, max_length=255)
    assessor_email: Optional[str] = Field(None, max_length=255)


class AssessmentResponse(AssessmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
