from fastapi import FastAPI

from app.routers import health, companies, assessments

app = FastAPI()

app.include_router(health.router)
app.include_router(companies.router)
app.include_router(assessments.router)
