from fastapi import Depends, HTTPException
from azure.cosmos import ContainerProxy
from app.core.database import get_container
from app.models.frontend_project import GetFrontendProjectResponse


class FrontendProjectService:
    def __init__(self, frontend_projects_container: ContainerProxy):
        self.frontend_projects_container = frontend_projects_container

    async def get_frontend_project_by_id(
        self, frontend_project_id: str
    ) -> GetFrontendProjectResponse:
        """Retrieve a frontend project by its ID.

        Args:
            frontend_project_id (str): The ID of the frontend project to retrieve.
            frontend_projects_container (ContainerProxy): The container client for the frontend projects.

        Returns:
            GetFrontendProjectResponse: The frontend project data.

        Raises:
            HTTPException: If the frontend project is not found or if there is a validation error.
        """
        # Query parameters for CosmosDB
        query = "SELECT * FROM c WHERE c.id = @frontend_project_id"
        params = [{"name": "@frontend_project_id", "value": frontend_project_id}]

        # Query the container
        query_results = list(
            self.frontend_projects_container.query_items(
                query=query, parameters=params, enable_cross_partition_query=True
            )
        )

        # Check if project exists
        if not query_results:
            raise HTTPException(
                status_code=404,
                detail=f"Frontend Project with ID {frontend_project_id} not found.",
            )

        # Get the first (and only) result
        frontend_project_data = query_results[0]

        # Validate the response data agains Pydantic model
        try:
            return GetFrontendProjectResponse(**frontend_project_data)
        except Exception as e:
            print(f"Validation error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Frontend Project data does not match expected schema",
            )


async def get_frontend_project_container():
    """Get the container client for the frontend projects."""
    return await get_container("frontend-projects")


async def get_frontend_project_service(
    frontend_projects_container: ContainerProxy = Depends(
        get_frontend_project_container
    ),
) -> FrontendProjectService:
    return FrontendProjectService(frontend_projects_container)
