from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def read_root():
    return "NOT_IMPLEMENTED"

@app.post("/api/v1/companies")
def create_company():
    return "NOT_IMPLEMENTED"

@app.get("/api/v1/companies")
def list_companies():
    return "NOT_IMPLEMENTED"

@app.get("/api/v1/companies/{company_id}")
def get_company(company_id: str):
    return "NOT_IMPLEMENTED"

@app.put("/api/v1/companies/{company_id}")
def update_company(company_id: str):
    return "NOT_IMPLEMENTED"

@app.delete("/api/v1/companies/{company_id}")
def delete_company(company_id: str):
    return "NOT_IMPLEMENTED"

@app.post("/api/v1/assessments")
def create_assessment():
    return "NOT_IMPLEMENTED"

@app.get("/api/v1/assessments")
def list_assessments():
    return "NOT_IMPLEMENTED"

@app.get("/api/v1/assessments/{assessment_id}")
def get_assessment(assessment_id: str):
    return "NOT_IMPLEMENTED"

@app.patch("/api/v1/assessments/{assessment_id}")
def update_assessment(assessment_id: str):
    return "NOT_IMPLEMENTED"

@app.post("/api/v1/assessments/{assessment_id}/scores")
def add_scores(assessment_id: str):
    return "NOT_IMPLEMENTED"

@app.get("/api/v1/assessments/{assessment_id}/scores")
def get_scores(assessment_id: str):
    return "NOT_IMPLEMENTED"

@app.put("/api/v1/assessments/{assessment_id}/scores")
def update_scores(assessment_id: str):
    return "NOT_IMPLEMENTED"