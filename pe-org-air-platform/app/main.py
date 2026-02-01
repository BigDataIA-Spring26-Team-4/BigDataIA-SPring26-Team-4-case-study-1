from fastapi import FastAPI, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.models.assessment import AssessmentCreate, AssessmentUpdate, AssessmentResponse
from app.models.dimension import DimensionScoreCreate, DimensionScoreUpdate, DimensionScoreResponse
from app.services import snowflake


app = FastAPI()


def get_db():
    return snowflake.get_db()


@app.get("/health")
def show_health() -> dict:
    return {"status": "ok"}


@app.post("/api/v1/companies", response_model=CompanyResponse)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    return snowflake.create_company(db, company)


@app.get("/api/v1/companies", response_model=list[CompanyResponse])
def list_companies(db: Session = Depends(get_db)):
    return snowflake.list_companies(db)


@app.get("/api/v1/companies/{company_id}", response_model=CompanyResponse)
def get_company(company_id: UUID, db: Session = Depends(get_db)):
    return snowflake.get_company(db, str(company_id))


@app.put("/api/v1/companies/{company_id}", response_model=CompanyResponse)
def update_company(company_id: UUID, company: CompanyUpdate, db: Session = Depends(get_db)):
    return snowflake.update_company(db, str(company_id), company)


@app.delete("/api/v1/companies/{company_id}")
def delete_company(company_id: UUID, db: Session = Depends(get_db)):
    snowflake.delete_company(db, str(company_id))
    return {"detail": "deleted"}


@app.post("/api/v1/assessments", response_model=AssessmentResponse)
def create_assessment(assessment: AssessmentCreate, db: Session = Depends(get_db)):
    return snowflake.create_assessment(db, assessment)


@app.get("/api/v1/assessments", response_model=list[AssessmentResponse])
def list_assessments(db: Session = Depends(get_db)):
    return snowflake.list_assessments(db)


@app.get("/api/v1/assessments/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(assessment_id: UUID, db: Session = Depends(get_db)):
    return snowflake.get_assessment(db, str(assessment_id))


@app.patch("/api/v1/assessments/{assessment_id}", response_model=AssessmentResponse)
def update_assessment(assessment_id: UUID, assessment: AssessmentUpdate, db: Session = Depends(get_db)):
    return snowflake.update_assessment(db, str(assessment_id), assessment)


@app.post("/api/v1/assessments/{assessment_id}/scores", response_model=list[DimensionScoreResponse])
def add_scores(assessment_id: UUID, scores: list[DimensionScoreCreate], db: Session = Depends(get_db)):
    return snowflake.add_scores(db, str(assessment_id), scores)


@app.get("/api/v1/assessments/{assessment_id}/scores", response_model=list[DimensionScoreResponse])
def get_scores(assessment_id: UUID, db: Session = Depends(get_db)):
    return snowflake.get_scores(db, str(assessment_id))


@app.put("/api/v1/assessments/{assessment_id}/scores", response_model=list[DimensionScoreResponse])
def update_scores(assessment_id: UUID, scores: list[DimensionScoreUpdate], db: Session = Depends(get_db)):
    return snowflake.update_scores(db, str(assessment_id), scores)
