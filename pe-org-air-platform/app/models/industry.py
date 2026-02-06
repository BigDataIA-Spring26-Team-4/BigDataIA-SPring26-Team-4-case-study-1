from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class IndustryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sector: str = Field(..., min_length=1, max_length=100)
    h_r_base: float = Field(..., ge=0.0, le=100.0)


class IndustryCreate(IndustryBase):
    pass


class IndustryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sector: Optional[str] = Field(None, min_length=1, max_length=100)
    h_r_base: Optional[float] = Field(None, ge=0.0, le=100.0)


class IndustryResponse(IndustryBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
