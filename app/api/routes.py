from fastapi import APIRouter
from app.api.endpoints import count

# Create the main router
router = APIRouter()

# Include the count router 
router.include_router(
    count.router, 
    prefix="/count", 
    tags=["count"]
)


# Add health check endpoint
@router.get("/health")
async def health_check():
    return {"status": "healthy"}

# Add basic root endpoint
@router.get("/")
async def root():
    return {"message": "Welcome to the Count API"}
