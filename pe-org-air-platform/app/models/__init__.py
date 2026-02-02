"""
Pydantic Models Package for PE Org-AI-R Platform
Central exports for all data models

This package provides all Pydantic models used throughout the application.
Import models from here rather than individual files for consistency.

Example:
    >>> from app.models import CompanyCreate, AssessmentResponse
    >>> company = CompanyCreate(name="TechCorp", ...)
"""

# Assessment models
from .assessment import (
    AssessmentType,
    AssessmentStatus,
    AssessmentBase,
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentResponse,
)

# Company models
from .company import (
    CompanyBase,
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    IndustryResponse,
)

# Dimension models
from .dimension import (
    Dimension,
    DIMENSION_WEIGHTS,
    DimensionScoreBase,
    DimensionScoreCreate,
    DimensionScoreUpdate,
    DimensionScoreResponse,
    validate_dimension_coverage,
    calculate_weighted_score,
)

# Common models
from .common import (
    PaginatedResponse,
    HealthResponse,
    ErrorResponse,
    MessageResponse,
)


# Define what gets exported when someone does: from app.models import *
__all__ = [
    # Assessment
    "AssessmentType",
    "AssessmentStatus",
    "AssessmentBase",
    "AssessmentCreate",
    "AssessmentUpdate",
    "AssessmentResponse",
    
    # Company
    "CompanyBase",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    "IndustryResponse",
    
    # Dimension
    "Dimension",
    "DIMENSION_WEIGHTS",
    "DimensionScoreBase",
    "DimensionScoreCreate",
    "DimensionScoreUpdate",
    "DimensionScoreResponse",
    "validate_dimension_coverage",
    "calculate_weighted_score",
    
    # Common
    "PaginatedResponse",
    "HealthResponse",
    "ErrorResponse",
    "MessageResponse",
]