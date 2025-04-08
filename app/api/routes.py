from fastapi import APIRouter
from app.api.endpoints import frontend_projects, health, predictions

# Create the main router
router = APIRouter()

# Include routers from different modules
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(
    frontend_projects.router, prefix="/frontend-projects", tags=["frontend-projects"]
)
router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])


# Add basic root endpoint
@router.get("/")
async def root():
    return {"message": "Welcome to the Count API"}
