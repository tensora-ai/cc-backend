from fastapi import APIRouter
from app.api.endpoints import count

router = APIRouter()

router.include_router(count.router, prefix="/count", tags=["count"])


@router.get("/")
async def root():
    return {"message": "Welcome to the Count API"}
