from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class Dimension(str, Enum):
    DATA_INFRASTRUCTURE = "data_infrastructure"
    AI_GOVERNANCE = "ai_governance"
    TECHNOLOGY_STACK = "technology_stack"
    TALENT_SKILLS = "talent_skills"
    LEADERSHIP_VISION = "leadership_vision"
    USE_CASE_PORTFOLIO = "use_case_portfolio"
    CULTURE_CHANGE = "culture_change"


DIMENSION_DEFAULT_WEIGHTS: dict[Dimension, float] = {
    Dimension.DATA_INFRASTRUCTURE: 0.20,
    Dimension.AI_GOVERNANCE: 0.20,
    Dimension.TECHNOLOGY_STACK: 0.25,
    Dimension.TALENT_SKILLS: 0.20,
    Dimension.LEADERSHIP_VISION: 0.15,
}


class DimensionScoreBase(BaseModel):
    assessment_id: UUID
    dimension: Dimension
    score: float = Field(..., ge=0.0, le=100.0)
    weight: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence_count: int = Field(..., ge=0)


class DimensionScoreCreate(DimensionScoreBase):
    pass


class DimensionScoreUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=0.0, le=100.0)
    weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    evidence_count: Optional[int] = Field(None, ge=0)


class DimensionScoreResponse(DimensionScoreBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
