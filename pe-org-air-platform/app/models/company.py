"""
Company and Industry Models for PE Org-AI-R Platform

This module defines:
- Company models (create, update, response)
- Industry reference data models
- Ticker symbol validation
- Position factor constraints
"""

from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional


class CompanyBase(BaseModel):
    """
    Base company fields shared across models
    
    Position factor represents strategic importance:
    - Positive values (0 to 1): Strategic priority/opportunity
    - Negative values (-1 to 0): Risk/concern indicator
    - Zero (0): Neutral position
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Company name (required, 1-255 characters)"
    )
    ticker: Optional[str] = Field(
        None,
        max_length=10,
        description="Stock ticker symbol (optional, uppercase, max 10 chars)"
    )
    industry_id: UUID = Field(
        ...,
        description="UUID reference to industries table"
    )
    position_factor: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Strategic position indicator (-1.0 to 1.0)"
    )

    @field_validator('ticker')
    @classmethod
    def uppercase_ticker(cls, v: Optional[str]) -> Optional[str]:
        """
        Convert ticker to uppercase
        
        Stock tickers are conventionally uppercase (e.g., AAPL, MSFT)
        This validator ensures consistency
        
        Args:
            v: Ticker symbol input
            
        Returns:
            Uppercase ticker or None
        """
        return v.upper() if v else None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Validate and clean company name
        
        Ensures name is not just whitespace
        Strips leading/trailing whitespace
        """
        v = v.strip()
        if not v:
            raise ValueError('Company name cannot be empty or only whitespace')
        return v


class CompanyCreate(CompanyBase):
    """
    Schema for creating a new company
    
    Use this when POST-ing to /api/v1/companies
    All base fields required except ticker and position_factor (has default)
    """
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "TechCorp Industries",
                "ticker": "TECH",
                "industry_id": "550e8400-e29b-41d4-a716-446655440006",
                "position_factor": 0.5
            }
        }


class CompanyUpdate(BaseModel):
    """
    Schema for updating a company
    
    Use this when PUT-ing to /api/v1/companies/{id}
    All fields are optional - only provided fields will be updated
    """
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated company name"
    )
    ticker: Optional[str] = Field(
        None,
        max_length=10,
        description="Updated ticker symbol"
    )
    industry_id: Optional[UUID] = Field(
        None,
        description="Updated industry reference"
    )
    position_factor: Optional[float] = Field(
        None,
        ge=-1.0,
        le=1.0,
        description="Updated position factor"
    )

    @field_validator('ticker')
    @classmethod
    def uppercase_ticker(cls, v: Optional[str]) -> Optional[str]:
        """Convert ticker to uppercase"""
        return v.upper() if v else None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean name if provided"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Company name cannot be empty or only whitespace')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "TechCorp Industries Inc.",
                "position_factor": 0.7
            }
        }


class CompanyResponse(CompanyBase):
    """
    Schema for company responses
    
    Returned by all GET endpoints for companies
    Includes database-generated fields (id, timestamps)
    """
    id: UUID = Field(
        ...,
        description="Unique identifier for this company"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when company was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp of last update"
    )

    class Config:
        """Pydantic configuration"""
        from_attributes = True  # Allow ORM mode for database objects
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440010",
                "name": "TechCorp Industries",
                "ticker": "TECH",
                "industry_id": "550e8400-e29b-41d4-a716-446655440006",
                "position_factor": 0.5,
                "created_at": "2026-02-01T10:00:00Z",
                "updated_at": "2026-02-01T10:00:00Z"
            }
        }


class IndustryResponse(BaseModel):
    """
    Schema for industry reference data
    
    Industries are static reference data (seeded in database)
    Used for categorizing companies and applying industry benchmarks
    
    h_r_base: Hurdle Rate Base - minimum expected return for that industry
    """
    id: UUID = Field(
        ...,
        description="Unique identifier for this industry"
    )
    name: str = Field(
        ...,
        description="Industry name (e.g., 'Manufacturing', 'Healthcare Services')"
    )
    sector: str = Field(
        ...,
        description="Broader sector classification (e.g., 'Industrials', 'Healthcare')"
    )
    h_r_base: float = Field(
        ...,
        ge=0,
        le=100,
        description="Hurdle rate baseline for this industry (0-100)"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when industry was created"
    )

    class Config:
        """Pydantic configuration"""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440006",
                "name": "Technology",
                "sector": "Technology",
                "h_r_base": 85.0,
                "created_at": "2026-01-01T00:00:00Z"
            }
        }