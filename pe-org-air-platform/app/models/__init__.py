"""
Models package for PE Org-AI-R Platform.

This package contains all Pydantic models for data validation and serialization.
"""

from app.models.company import (
    CompanyBase,
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    IndustryBase,
    IndustryCreate,
    IndustryResponse,
)

from app.models.assessment import (
    AssessmentType,
    AssessmentStatus,
    AssessmentBase,
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentResponse,
    VALID_STATUS_TRANSITIONS,
    validate_status_transition,
    get_allowed_transitions,
)

from app.models.common import (
    PaginatedResponse,
    paginate,
)

from app.models.dimension import (
    Dimension,
    DimensionScoreBase,
    DimensionScoreCreate,
    DimensionScoreUpdate,
    DimensionScoreResponse,
    DIMENSION_WEIGHTS,
    DIMENSION_DESCRIPTIONS,
    get_dimension_weight,
    get_dimension_description,
    validate_dimension_scores_complete,
    get_missing_dimensions,
)

__all__ = [
    # Common models
    "PaginatedResponse",
    "paginate",
    
    # Company models
    "CompanyBase",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    "IndustryBase",
    "IndustryCreate",
    "IndustryResponse",
    
    # Assessment models
    "AssessmentType",
    "AssessmentStatus",
    "AssessmentBase",
    "AssessmentCreate",
    "AssessmentUpdate",
    "AssessmentResponse",
    "VALID_STATUS_TRANSITIONS",
    "validate_status_transition",
    "get_allowed_transitions",
    
    # Dimension models
    "Dimension",
    "DimensionScoreBase",
    "DimensionScoreCreate",
    "DimensionScoreUpdate",
    "DimensionScoreResponse",
    "DIMENSION_WEIGHTS",
    "DIMENSION_DESCRIPTIONS",
    "get_dimension_weight",
    "get_dimension_description",
    "validate_dimension_scores_complete",
    "get_missing_dimensions",
]
