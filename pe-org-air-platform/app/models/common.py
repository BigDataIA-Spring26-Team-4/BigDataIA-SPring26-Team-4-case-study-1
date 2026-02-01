"""
Common Models for PE Org-AI-R Platform
Shared response models and utilities

This module defines:
- Generic paginated response wrapper
- Health check response structure
- Standard error response format
"""

from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional
from datetime import datetime, timezone


# Generic type variable for pagination
T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper
    
    Used for all list endpoints that support pagination
    Provides consistent pagination structure across the API
    
    Type Parameters:
        T: The type of items being paginated (e.g., CompanyResponse)
    
    Example:
        >>> from app.models import CompanyResponse
        >>> response = PaginatedResponse[CompanyResponse](
        ...     items=[company1, company2],
        ...     total=50,
        ...     page=1,
        ...     page_size=20,
        ...     total_pages=3
        ... )
    """
    items: List[T] = Field(
        ...,
        description="List of items for current page"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of items across all pages"
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number (1-indexed)"
    )
    page_size: int = Field(
        ...,
        ge=1,
        description="Number of items per page"
    )
    total_pages: int = Field(
        ...,
        ge=0,
        description="Total number of pages"
    )

    @property
    def has_next(self) -> bool:
        """
        Check if there's a next page
        
        Returns:
            True if current page < total pages
        """
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """
        Check if there's a previous page
        
        Returns:
            True if current page > 1
        """
        return self.page > 1
    
    @property
    def next_page(self) -> Optional[int]:
        """
        Get next page number
        
        Returns:
            Next page number or None if on last page
        """
        return self.page + 1 if self.has_next else None
    
    @property
    def prev_page(self) -> Optional[int]:
        """
        Get previous page number
        
        Returns:
            Previous page number or None if on first page
        """
        return self.page - 1 if self.has_prev else None

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "items": [
                    {"id": "...", "name": "Company 1"},
                    {"id": "...", "name": "Company 2"}
                ],
                "total": 50,
                "page": 1,
                "page_size": 20,
                "total_pages": 3
            }
        }


class HealthResponse(BaseModel):
    """
    Health check response structure
    
    Used by /health endpoint to report system status
    Includes dependency health checks (Snowflake, Redis, S3)
    
    Status values:
    - "healthy": All systems operational
    - "degraded": Some systems down but core functionality available
    - "unhealthy": Critical systems down
    """
    status: str = Field(
        ...,
        description="Overall system status: 'healthy', 'degraded', or 'unhealthy'"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of health check"
    )
    version: str = Field(
        ...,
        description="API version"
    )
    dependencies: dict[str, str] = Field(
        ...,
        description="Health status of each dependency service"
    )
    
    @property
    def is_healthy(self) -> bool:
        """Check if system is fully healthy"""
        return self.status == "healthy"
    
    @property
    def failed_dependencies(self) -> list[str]:
        """Get list of failed dependencies"""
        return [
            service for service, status in self.dependencies.items()
            if status != "healthy"
        ]

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-02-01T12:00:00Z",
                "version": "1.0.0",
                "dependencies": {
                    "snowflake": "healthy",
                    "redis": "healthy",
                    "s3": "healthy"
                }
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response format
    
    Provides consistent error structure across the API
    Used by exception handlers to return user-friendly errors
    
    HTTP status codes should be set separately
    This model is just for the response body
    """
    detail: str = Field(
        ...,
        description="Human-readable error message"
    )
    error_code: Optional[str] = Field(
        None,
        description="Machine-readable error code (e.g., 'COMPANY_NOT_FOUND')"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when error occurred"
    )
    path: Optional[str] = Field(
        None,
        description="API path where error occurred"
    )
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "detail": "Company with id 550e8400-... not found",
                "error_code": "COMPANY_NOT_FOUND",
                "timestamp": "2026-02-01T12:00:00Z",
                "path": "/api/v1/companies/550e8400-..."
            }
        }


class MessageResponse(BaseModel):
    """
    Simple message response
    
    Used for endpoints that don't return data
    (e.g., successful DELETE operations)
    """
    message: str = Field(
        ...,
        description="Success or info message"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of response"
    )
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "message": "Company deleted successfully",
                "timestamp": "2026-02-01T12:00:00Z"
            }
        }