from fastapi import APIRouter, Depends, HTTPException
from azure.cosmos import ContainerProxy
from app.core.database import get_container
from app.models.count import AddCountsInput, AddCountsOutput
from app.models.health import HealthCheckResponse
from app.models.project import GetProjectResponse
from app.resources import app_resources
from app.services.project_service import ProjectService, get_project_service

router = APIRouter()


@router.get("/", response_model=HealthCheckResponse)
async def get_health_status() -> HealthCheckResponse:
    """Retrieve the health status of the service.

    Returns:
        HealthCheckResponse: Health status response.
    """

    # Simply return healthy for now
    # In the future, we can add checks for database connectivity, etc.
    return HealthCheckResponse(status="healthy", message="Service is running smoothly.")
