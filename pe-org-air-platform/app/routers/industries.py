import math
import structlog
from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.industry import IndustryCreate, IndustryUpdate, IndustryResponse
from app.services import snowflake
from app.services.snowflake import get_db
from app.services.redis_cache import cached, invalidate
from app.utils.pagination import PaginatedResponse

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v1/industries", tags=["industries"])

CACHE_PREFIX = "industries:"


@router.post("", response_model=IndustryResponse)
def create_industry(industry: IndustryCreate, db: Session = Depends(get_db)):
    log.info("creating_industry", name=industry.name)
    result = snowflake.create_industry(db, industry)
    invalidate(CACHE_PREFIX)
    log.info("industry_created", industry_id=result.id)
    return result


@router.get("", response_model=PaginatedResponse[IndustryResponse])
@cached(prefix=CACHE_PREFIX, exclude=["db"], ttl=3600)  # 1 hour
def list_industries(page: int = 1, page_size: int = 50, db: Session = Depends(get_db)):
    log.info("listing_industries", page=page, page_size=page_size)

    # Validate and cap page_size
    if page_size > 100:
        page_size = 100
    if page < 1:
        page = 1

    items, total_count = snowflake.list_industries(db, page, page_size)
    total_pages = math.ceil(total_count / page_size) if page_size > 0 else 0

    return PaginatedResponse(
        items=items,
        page=page,
        page_size=page_size,
        total_count=total_count,
        total_pages=total_pages
    )


@router.get("/{industry_id}", response_model=IndustryResponse)
@cached(prefix=CACHE_PREFIX, exclude=["db"], ttl=3600)  # 1 hour
def get_industry(industry_id: UUID, db: Session = Depends(get_db)):
    log.info("getting_industry", industry_id=str(industry_id))
    return snowflake.get_industry(db, str(industry_id))


@router.put("/{industry_id}", response_model=IndustryResponse)
def update_industry(industry_id: UUID, industry: IndustryUpdate, db: Session = Depends(get_db)):
    log.info("updating_industry", industry_id=str(industry_id))
    result = snowflake.update_industry(db, str(industry_id), industry)
    invalidate(CACHE_PREFIX)
    log.info("industry_updated", industry_id=str(industry_id))
    return result


@router.delete("/{industry_id}")
def delete_industry(industry_id: UUID, db: Session = Depends(get_db)):
    log.info("deleting_industry", industry_id=str(industry_id))
    snowflake.delete_industry(db, str(industry_id))
    invalidate(CACHE_PREFIX)
    log.info("industry_deleted", industry_id=str(industry_id))
    return {"detail": "deleted"}
