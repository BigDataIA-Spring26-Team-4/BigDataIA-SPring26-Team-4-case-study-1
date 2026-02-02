from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def show_health() -> dict:
    return {"status": "ok"}
