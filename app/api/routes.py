from fastapi import APIRouter
from app.api.endpoints import health_check, projects, blobs

# Create the main router
router = APIRouter()

# Include routers from different modules
router.include_router(health_check.router, prefix="/health", tags=["health"])
router.include_router(projects.router, prefix="/projects", tags=["projects"])
router.include_router(blobs.router, prefix="/blobs", tags=["blobs"])


# Add basic root endpoint
@router.get("/")
async def root():
    return {"message": "Welcome to the Tensora Count Backend API"}
