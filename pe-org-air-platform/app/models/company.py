from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime


class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    ticker: Optional[str] = Field(None, max_length=10)
    industry_id: UUID
    position_factor: float = Field(0.0, ge=-1.0, le=1.0)

    @field_validator('ticker')
    @classmethod
    def uppercase_ticker(cls, v: Optional[str]) -> Optional[str]:
        return v.upper() if v else None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    ticker: Optional[str] = Field(None, max_length=10)
    industry_id: Optional[UUID] = None
    position_factor: Optional[float] = Field(None, ge=-1.0, le=1.0)

    @field_validator('ticker')
    @classmethod
    def uppercase_ticker(cls, v: Optional[str]) -> Optional[str]:
        return v.upper() if v else None


class CompanyResponse(CompanyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
