from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import companies, assessments, health

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Readiness Assessment Platform for Private Equity",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    health.router,
    tags=["Health"]
)

app.include_router(
    companies.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Companies"]
)

app.include_router(
    assessments.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Assessments"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PE Org-AI-R Platform API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )