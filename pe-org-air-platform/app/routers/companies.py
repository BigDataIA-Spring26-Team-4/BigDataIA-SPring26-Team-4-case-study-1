from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.services import snowflake
from app.services.snowflake import get_db
from app.services.redis_cache import cached, invalidate

router = APIRouter(prefix="/api/v1/companies", tags=["companies"])

CACHE_PREFIX = "companies:"


@router.post("", response_model=CompanyResponse)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    result = snowflake.create_company(db, company)
    invalidate(CACHE_PREFIX)
    return result


@router.get("", response_model=list[CompanyResponse])
@cached(prefix=CACHE_PREFIX)
def list_companies(db: Session = Depends(get_db)):
    return snowflake.list_companies(db)


@router.get("/{company_id}", response_model=CompanyResponse)
@cached(prefix=CACHE_PREFIX)
def get_company(company_id: UUID, db: Session = Depends(get_db)):
    return snowflake.get_company(db, str(company_id))


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(company_id: UUID, company: CompanyUpdate, db: Session = Depends(get_db)):
    result = snowflake.update_company(db, str(company_id), company)
    invalidate(CACHE_PREFIX)
    return result


@router.delete("/{company_id}")
def delete_company(company_id: UUID, db: Session = Depends(get_db)):
    snowflake.delete_company(db, str(company_id))
    invalidate(CACHE_PREFIX)
    return {"detail": "deleted"}
