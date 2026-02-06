from pydantic import BaseModel, Field, model_validator
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


DIMENSION_WEIGHTS: dict[Dimension, float] = {
    Dimension.DATA_INFRASTRUCTURE: 0.25,
    Dimension.AI_GOVERNANCE: 0.20,
    Dimension.TECHNOLOGY_STACK: 0.15,
    Dimension.TALENT_SKILLS: 0.15,
    Dimension.LEADERSHIP_VISION: 0.10,
    Dimension.USE_CASE_PORTFOLIO: 0.10,
    Dimension.CULTURE_CHANGE: 0.05,
}


class DimensionScoreBase(BaseModel):
    assessment_id: UUID
    dimension: Dimension
    score: float = Field(..., ge=0.0, le=100.0)
    weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    evidence_count: int = Field(default=0, ge=0)

    @model_validator(mode='after')
    def set_default_weight(self) -> 'DimensionScoreBase':
        if self.weight is None:
            self.weight = DIMENSION_WEIGHTS.get(self.dimension, 0.1)
        return self


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
