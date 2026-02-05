"""
Industries API router for PE Org-AI-R Platform.

Provides endpoints for industry reference data with caching.
Per PDF Section 8.1: "Redis caching implemented for companies and industries"
"""

import structlog
from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.company import IndustryResponse
from app.services import snowflake
from app.services.snowflake import get_db
from app.services.redis_cache import cached

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v1/industries", tags=["industries"])

# Industry list cached for 1 hour (PDF Table 3)
CACHE_PREFIX = "industries:"


@router.get("", response_model=list[IndustryResponse])
@cached(prefix=CACHE_PREFIX, ttl=3600)  # 1 hour per PDF Table 3
def list_industries(db: Session = Depends(get_db)):
    """
    List all industries.
    
    Cached for 1 hour per PDF Section 6.1 Table 3:
    "Industry list - 1 hour - Static reference data"
    """
    log.info("listing_industries")
    return snowflake.list_industries(db)


@router.get("/{industry_id}", response_model=IndustryResponse)
@cached(prefix=CACHE_PREFIX, ttl=3600)  # 1 hour
def get_industry(industry_id: UUID, db: Session = Depends(get_db)):
    """Get industry by ID (cached)."""
    log.info("getting_industry", industry_id=str(industry_id))
    return snowflake.get_industry(db, str(industry_id))
