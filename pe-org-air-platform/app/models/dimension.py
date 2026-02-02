"""
Dimension Score Models for PE Org-AI-R Platform
Dimension scoring data structures

This module defines:
- Seven dimensions of AI-readiness (enum)
- Default weights for each dimension
- Dimension score models (create, update, response)
- Automatic weight assignment based on dimension
"""

from pydantic import BaseModel, Field, model_validator
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum


class Dimension(str, Enum):
    """
    Seven dimensions of AI-readiness from PE Org-AI-R framework
    
    Each dimension measures a different aspect of organizational AI capability:
    
    D1: DATA_INFRASTRUCTURE - Data quality, accessibility, governance
    D2: AI_GOVERNANCE - Policies, ethics frameworks, compliance
    D3: TECHNOLOGY_STACK - Cloud infrastructure, ML tooling, APIs
    D4: TALENT_SKILLS - AI/ML talent density, retention, training
    D5: LEADERSHIP_VISION - Executive commitment, AI strategy, investment
    D6: USE_CASE_PORTFOLIO - AI projects in production, pipeline, ROI
    D7: CULTURE_CHANGE - Innovation culture, change readiness, adoption
    """
    DATA_INFRASTRUCTURE = "data_infrastructure"
    AI_GOVERNANCE = "ai_governance"
    TECHNOLOGY_STACK = "technology_stack"
    TALENT_SKILLS = "talent_skills"
    LEADERSHIP_VISION = "leadership_vision"
    USE_CASE_PORTFOLIO = "use_case_portfolio"
    CULTURE_CHANGE = "culture_change"


# Default weights per dimension (from PE Org-AI-R framework)
# These sum to 1.0 (100%)
DIMENSION_WEIGHTS = {
    Dimension.DATA_INFRASTRUCTURE: 0.25,   # 25% - Most important
    Dimension.AI_GOVERNANCE: 0.20,         # 20% - Critical for compliance
    Dimension.TECHNOLOGY_STACK: 0.15,      # 15% - Infrastructure foundation
    Dimension.TALENT_SKILLS: 0.15,         # 15% - Human capital
    Dimension.LEADERSHIP_VISION: 0.10,     # 10% - Strategic direction
    Dimension.USE_CASE_PORTFOLIO: 0.10,    # 10% - Execution track record
    Dimension.CULTURE_CHANGE: 0.05,        # 5% - Supporting element
}


class DimensionScoreBase(BaseModel):
    """
    Base dimension score fields
    
    Each assessment should have exactly 7 dimension scores
    (one for each dimension in the Dimension enum)
    
    Evidence count tracks how many pieces of evidence support this score
    (useful for confidence calibration)
    """
    assessment_id: UUID = Field(
        ...,
        description="UUID of the assessment this score belongs to"
    )
    dimension: Dimension = Field(
        ...,
        description="Which dimension is being scored"
    )
    score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Score for this dimension (0-100)"
    )
    weight: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        description="Weight for this dimension (0-1), auto-set if not provided"
    )
    confidence: float = Field(
        default=0.8,
        ge=0,
        le=1,
        description="Confidence in this score (0-1), default 0.8"
    )
    evidence_count: int = Field(
        default=0,
        ge=0,
        description="Number of evidence items supporting this score"
    )

    @model_validator(mode='after')
    def set_default_weight(self) -> 'DimensionScoreBase':
        """
        Automatically set weight based on dimension if not provided
        
        Uses DIMENSION_WEIGHTS dictionary to assign framework-standard weights
        This ensures consistency across assessments unless explicitly overridden
        
        Returns:
            Self with weight set
        """
        if self.weight is None:
            self.weight = DIMENSION_WEIGHTS.get(self.dimension, 0.1)
        return self
    
    @model_validator(mode='after')
    def validate_score_evidence_relationship(self) -> 'DimensionScoreBase':
        """
        Validate that confidence aligns with evidence count
        
        More evidence should generally mean higher confidence
        This is a soft validation (warning, not error)
        """
        # High confidence (>0.9) with no evidence is suspicious
        if self.confidence > 0.9 and self.evidence_count == 0:
            # In production, you might log a warning here
            # For now, we allow it but note the inconsistency
            pass
        return self


class DimensionScoreCreate(DimensionScoreBase):
    """
    Schema for creating a dimension score
    
    Use this when POST-ing to /api/v1/assessments/{id}/scores
    Typically, you'll create all 7 scores at once (batch operation)
    """
    
    class Config:
        json_schema_extra = {
            "example": {
                "assessment_id": "550e8400-e29b-41d4-a716-446655440020",
                "dimension": "data_infrastructure",
                "score": 75.0,
                "confidence": 0.85,
                "evidence_count": 12
            }
        }


class DimensionScoreUpdate(BaseModel):
    """
    Schema for updating a dimension score
    
    Use this when PUT-ing to /api/v1/scores/{id}
    All fields optional - only provided fields will be updated
    """
    score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Updated score"
    )
    weight: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Updated weight"
    )
    confidence: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Updated confidence"
    )
    evidence_count: Optional[int] = Field(
        None,
        ge=0,
        description="Updated evidence count"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "score": 78.0,
                "confidence": 0.90,
                "evidence_count": 15
            }
        }


class DimensionScoreResponse(DimensionScoreBase):
    """
    Schema for dimension score responses
    
    Returned by all GET endpoints for dimension scores
    Includes database-generated fields (id, timestamp)
    """
    id: UUID = Field(
        ...,
        description="Unique identifier for this dimension score"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when score was created"
    )

    class Config:
        """Pydantic configuration"""
        from_attributes = True  # Allow ORM mode for database objects
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440030",
                "assessment_id": "550e8400-e29b-41d4-a716-446655440020",
                "dimension": "data_infrastructure",
                "score": 75.0,
                "weight": 0.25,
                "confidence": 0.85,
                "evidence_count": 12,
                "created_at": "2026-02-01T12:00:00Z"
            }
        }


# Utility function for validating a complete assessment
def validate_dimension_coverage(scores: list[DimensionScoreCreate]) -> bool:
    """
    Validate that all 7 dimensions are covered
    
    Each assessment should have exactly one score for each dimension
    
    Args:
        scores: List of dimension scores for an assessment
        
    Returns:
        True if all dimensions covered, False otherwise
        
    Example:
        >>> scores = [DimensionScoreCreate(...) for each dimension]
        >>> validate_dimension_coverage(scores)
        True
    """
    dimensions_present = {score.dimension for score in scores}
    all_dimensions = set(Dimension)
    return dimensions_present == all_dimensions


def calculate_weighted_score(scores: list[DimensionScoreResponse]) -> float:
    """
    Calculate weighted average score across all dimensions
    
    This is a simplified version of the VR score calculation
    (Full formula comes in Case Study 3)
    
    Args:
        scores: List of dimension scores for an assessment
        
    Returns:
        Weighted average score (0-100)
        
    Example:
        >>> scores = [score1, score2, ...]  # All 7 scores
        >>> vr_score = calculate_weighted_score(scores)
        >>> print(f"VR Score: {vr_score:.2f}")
        VR Score: 73.45
    """
    if not scores:
        return 0.0
    
    total_weighted_score = sum(score.score * score.weight for score in scores)
    total_weight = sum(score.weight for score in scores)
    
    # Normalize in case weights don't sum to 1.0
    return (total_weighted_score / total_weight) if total_weight > 0 else 0.0
