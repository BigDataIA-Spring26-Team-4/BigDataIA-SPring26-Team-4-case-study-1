"""
Assessment Models for PE Org-AI-R Platform
Assessment data structures and validation

This module defines all assessment-related models including:
- Assessment types and statuses (enums)
- Assessment creation, update, and response models
- Confidence interval validation
"""

from pydantic import BaseModel, Field, model_validator
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional
from enum import Enum


class AssessmentType(str, Enum):
    """
    Types of assessments conducted on portfolio companies
    
    - SCREENING: Quick external assessment for deal sourcing
    - DUE_DILIGENCE: Deep dive assessment with internal access
    - QUARTERLY: Regular monitoring of portfolio companies
    - EXIT_PREP: Pre-exit readiness assessment
    """
    SCREENING = "screening"
    DUE_DILIGENCE = "due_diligence"
    QUARTERLY = "quarterly"
    EXIT_PREP = "exit_prep"


class AssessmentStatus(str, Enum):
    """
    Assessment workflow states
    
    Workflow: DRAFT → IN_PROGRESS → SUBMITTED → APPROVED
    Special: SUPERSEDED (when a new assessment replaces an old one)
    """
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    SUPERSEDED = "superseded"


class AssessmentBase(BaseModel):
    """
    Base assessment fields shared across create/update/response models
    
    All assessments must be tied to a company and have a type.
    Assessor information is optional but recommended for audit trails.
    """
    company_id: UUID = Field(
        ...,
        description="UUID of the company being assessed"
    )
    assessment_type: AssessmentType = Field(
        ...,
        description="Type of assessment being conducted"
    )
    assessment_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Date when assessment was conducted"
    )
    primary_assessor: Optional[str] = Field(
        None,
        max_length=255,
        description="Name or ID of primary assessor"
    )
    secondary_assessor: Optional[str] = Field(
        None,
        max_length=255,
        description="Name or ID of secondary assessor (optional)"
    )


class AssessmentCreate(AssessmentBase):
    """
    Schema for creating a new assessment
    
    Use this when POST-ing to /api/v1/assessments
    All base fields are required except assessors
    """
    pass


class AssessmentUpdate(BaseModel):
    """
    Schema for updating assessment status
    
    Use this when PATCH-ing to /api/v1/assessments/{id}/status
    Only status can be updated via this endpoint
    """
    status: AssessmentStatus = Field(
        ...,
        description="New status for the assessment"
    )


class AssessmentResponse(AssessmentBase):
    """
    Schema for assessment responses
    
    Returned by all GET endpoints for assessments
    Includes calculated fields and timestamps
    """
    id: UUID = Field(
        ...,
        description="Unique identifier for this assessment"
    )
    status: AssessmentStatus = Field(
        default=AssessmentStatus.DRAFT,
        description="Current status of the assessment"
    )
    v_r_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Value-Readiness score (0-100), calculated in CS3"
    )
    confidence_lower: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Lower bound of confidence interval"
    )
    confidence_upper: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Upper bound of confidence interval"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when assessment was created"
    )

    @model_validator(mode='after')
    def validate_confidence_interval(self) -> 'AssessmentResponse':
        """
        Ensure confidence_upper >= confidence_lower
        
        Confidence intervals must be valid: upper bound >= lower bound
        This is a business rule validation
        
        Raises:
            ValueError: If confidence_upper < confidence_lower
        """
        if (self.confidence_upper is not None and 
            self.confidence_lower is not None and
            self.confidence_upper < self.confidence_lower):
            raise ValueError(
                f'confidence_upper ({self.confidence_upper}) must be >= '
                f'confidence_lower ({self.confidence_lower})'
            )
        return self

    class Config:
        """Pydantic configuration"""
        from_attributes = True  # Allow ORM mode for database objects
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "company_id": "550e8400-e29b-41d4-a716-446655440001",
                "assessment_type": "due_diligence",
                "assessment_date": "2026-02-01T12:00:00Z",
                "status": "in_progress",
                "primary_assessor": "John Smith",
                "secondary_assessor": "Jane Doe",
                "v_r_score": 78.5,
                "confidence_lower": 75.0,
                "confidence_upper": 82.0,
                "created_at": "2026-02-01T10:00:00Z"
            }
        }