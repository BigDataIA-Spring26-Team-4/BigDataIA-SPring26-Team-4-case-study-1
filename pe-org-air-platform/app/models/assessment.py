from pydantic import BaseModel, Field, model_validator
from typing import Optional
from uuid import UUID
from datetime import date, datetime, timezone
from enum import Enum


class AssessmentType(str, Enum):
    SCREENING = "screening"
    DUE_DILIGENCE = "due_diligence"
    QUARTERLY = "quarterly"
    EXIT_PREP = "exit_prep"


class AssessmentStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    SUPERSEDED = "superseded"


# Valid state transitions: status -> allowed next statuses
VALID_TRANSITIONS: dict[AssessmentStatus, list[AssessmentStatus]] = {
    AssessmentStatus.DRAFT: [AssessmentStatus.IN_PROGRESS, AssessmentStatus.SUPERSEDED],
    AssessmentStatus.IN_PROGRESS: [AssessmentStatus.SUBMITTED, AssessmentStatus.SUPERSEDED],
    AssessmentStatus.SUBMITTED: [AssessmentStatus.APPROVED, AssessmentStatus.SUPERSEDED],
    AssessmentStatus.APPROVED: [AssessmentStatus.SUPERSEDED],
    AssessmentStatus.SUPERSEDED: [],
}


class AssessmentBase(BaseModel):
    company_id: UUID
    type: AssessmentType
    assessment_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: AssessmentStatus = AssessmentStatus.DRAFT
    vr_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    confidence_lower: Optional[float] = Field(None, ge=0.0, le=100.0)
    confidence_upper: Optional[float] = Field(None, ge=0.0, le=100.0)
    primary_assessor: Optional[str] = Field(None, max_length=255)
    secondary_assessor: Optional[str] = Field(None, max_length=255)


class AssessmentCreate(AssessmentBase):
    pass


class AssessmentUpdate(BaseModel):
    type: Optional[AssessmentType] = None
    assessment_date: Optional[datetime] = None
    status: Optional[AssessmentStatus] = None
    vr_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    confidence_lower: Optional[float] = Field(None, ge=0.0, le=100.0)
    confidence_upper: Optional[float] = Field(None, ge=0.0, le=100.0)
    primary_assessor: Optional[str] = Field(None, max_length=255)
    secondary_assessor: Optional[str] = Field(None, max_length=255)


class AssessmentResponse(AssessmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    @model_validator(mode='after')
    def validate_confidence_interval(self) -> 'AssessmentResponse':
        if (self.confidence_upper is not None and
            self.confidence_lower is not None and
            self.confidence_upper < self.confidence_lower):
            raise ValueError('confidence_upper must be >= confidence_lower')
        return self

    model_config = {"from_attributes": True}
