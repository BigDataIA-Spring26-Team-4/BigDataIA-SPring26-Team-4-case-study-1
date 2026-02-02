from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.services import snowflake
from app.services.snowflake import get_db

router = APIRouter(prefix="/api/v1/companies", tags=["companies"])


@router.post("", response_model=CompanyResponse)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    return snowflake.create_company(db, company)


@router.get("", response_model=list[CompanyResponse])
def list_companies(db: Session = Depends(get_db)):
    return snowflake.list_companies(db)


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: UUID, db: Session = Depends(get_db)):
    return snowflake.get_company(db, str(company_id))


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(company_id: UUID, company: CompanyUpdate, db: Session = Depends(get_db)):
    return snowflake.update_company(db, str(company_id), company)


@router.delete("/{company_id}")
def delete_company(company_id: UUID, db: Session = Depends(get_db)):
    snowflake.delete_company(db, str(company_id))
    return {"detail": "deleted"}
