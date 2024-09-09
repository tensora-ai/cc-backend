from fastapi import APIRouter
from app.api.endpoints import count

# Create the main router
router = APIRouter()

# Include the profiles router
router.include_router(
    count.router,
    prefix="/count",
    tags=["count"]
)

# Add basic root endpoint
@router.get("/")
async def root():
    return {"message": "Welcome to the Count API"}