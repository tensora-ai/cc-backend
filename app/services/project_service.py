from fastapi import Depends, HTTPException
from azure.cosmos import ContainerProxy
from app.core.database import get_container
from app.models.project import GetProjectResponse


async def get_project_service(
    projects_container: ContainerProxy = Depends(
        lambda: get_container("frontend-projects")
    ),
):
    return ProjectService(projects_container)


class ProjectService:
    def __init__(self, projects_container: ContainerProxy):
        self.projects_container = projects_container

    async def get_project_by_id(self, project_id: str) -> GetProjectResponse:
        """Retrieve a project by its ID.

        Args:
            project_id (str): The ID of the project to retrieve.
            projects_container (ContainerProxy): The container client for the projects.

        Returns:
            GetProjectResponse: The project data.

        Raises:
            HTTPException: If the project is not found or if there is a validation error.
        """
        # Query parameters for CosmosDB
        query = "SELECT * FROM c WHERE c.id = @project_id"
        params = [{"name": "@project_id", "value": project_id}]

        # Query the container
        query_results = list(
            self.projects_container.query_items(
                query=query, parameters=params, enable_cross_partition_query=True
            )
        )

        # Check if project exists
        if not query_results:
            raise HTTPException(
                status_code=404, detail=f"Project with ID {project_id} not found."
            )

        # Get the first (and only) result
        project_data = query_results[0]

        # Validate the response data agains Pydantic model
        try:
            return GetProjectResponse(**project_data)
        except Exception as e:
            print(f"Validation error: {e}")
            raise HTTPException(
                status_code=500, detail="Project data does not match expected schema"
            )
