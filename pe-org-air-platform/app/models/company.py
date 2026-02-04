from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    ticker: Optional[str] = Field(None, pattern=r"^[A-Z]{1,10}$")
    industry_id: UUID
    position: float = Field(0.0, ge=-1.0, le=1.0)


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    ticker: Optional[str] = Field(None, pattern=r"^[A-Z]{1,10}$")
    industry_id: Optional[UUID] = None
    position: Optional[float] = Field(None, ge=-1.0, le=1.0)


class CompanyResponse(CompanyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
