from fastapi import APIRouter
from app.api.endpoints import frontend_projects, health_check, predictions, images

# Create the main router
router = APIRouter()

# Include routers from different modules
router.include_router(health_check.router, prefix="/health", tags=["health"])
router.include_router(
    frontend_projects.router, prefix="/frontend-projects", tags=["frontend-projects"]
)
router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
router.include_router(images.router, prefix="/images", tags=["images"])


# Add basic root endpoint
@router.get("/")
async def root():
    return {"message": "Welcome to the Count API"}
