from fastapi import APIRouter, Depends, HTTPException
from azure.cosmos import ContainerProxy
from app.core.database import get_container
from app.models.count import AddCountsInput, AddCountsOutput
from app.models.frontend_project import GetFrontendProjectResponse
from app.resources import app_resources
from app.services.frontend_project_service import (
    FrontendProjectService,
    get_frontend_project_service,
)

router = APIRouter()


@router.get("/{frontend_project_id}", response_model=GetFrontendProjectResponse)
async def get_frontend_project(
    frontend_project_id: str,
    frontend_project_service: FrontendProjectService = Depends(
        get_frontend_project_service
    ),
) -> GetFrontendProjectResponse:
    """Retrieve a frontend project by its ID.

    Args:
        frontend_project_id (str): The ID of the frontend project to retrieve.
        frontend_projects_container (ContainerProxy): The container client for the frontend projects.

    Returns:
        GetFrontendProjectResponse: The project data.
    """
    return await frontend_project_service.get_frontend_project_by_id(
        frontend_project_id
    )
