from fastapi import APIRouter, Depends, HTTPException
from azure.cosmos import ContainerProxy
from app.core.database import get_container
from app.models.count import AddCountsInput, AddCountsOutput
from app.models.project import GetProjectResponse
from app.resources import app_resources
from app.services.project_service import ProjectService, get_project_service

router = APIRouter()


@router.get("/{project_id}", response_model=GetProjectResponse)
async def get_project(
    project_id: str, project_service: ProjectService = Depends(get_project_service)
) -> GetProjectResponse:
    """Retrieve a project by its ID.

    Args:
        project_id (str): The ID of the project to retrieve.
        projects_container (ContainerProxy): The container client for the projects.

    Returns:
        GetProjectResponse: The project data.
    """
    return await project_service.get_project_by_id(project_id)
