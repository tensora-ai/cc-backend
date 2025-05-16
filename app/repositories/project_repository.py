from typing import List, Optional, Dict, Any
from azure.cosmos import ContainerProxy
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from app.core.logging import get_logger
from app.models.prediction import AreaMapping, CameraPosition, ProjectMapping


class ProjectRepository:
    """Repository for basic CRUD operations on projects."""

    def __init__(self, projects_container: ContainerProxy):
        self.container = projects_container
        self.logger = get_logger(__name__)

    async def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects as raw dictionaries."""
        query = "SELECT * FROM c"
        items = self.container.query_items(
            query=query, enable_cross_partition_query=True
        )

        return list(items)

    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a project by ID as a raw dictionary."""
        try:
            item = await self.container.read_item(
                item=project_id, partition_key=project_id
            )
            return item
        except CosmosResourceNotFoundError:
            return None

    async def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project."""
        created_item = await self.container.create_item(body=project_data)
        return created_item

    async def update_project(
        self, project_id: str, project_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a project."""
        try:
            # Replace the entire document
            updated_item = await self.container.replace_item(
                item=project_id, body=project_data
            )

            return updated_item
        except CosmosResourceNotFoundError:
            return None

    async def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        try:
            await self.container.delete_item(item=project_id, partition_key=project_id)
            return True
        except CosmosResourceNotFoundError:
            return False

    async def get_camera_mappings(self) -> Dict[str, ProjectMapping]:
        """
        Extract project metadata and create structured mappings.

        Returns:
            Dict mapping project_id -> ProjectMapping objects
        """
        project_mappings = {}

        # Extract all project metadata with a single query
        query = "SELECT c.id, c.cameras FROM c"
        query_results = await self.container.query_items(
            query=query, enable_cross_partition_query=True
        ).to_list()

        for project in query_results:
            project_id = project["id"]
            areas_dict = {}

            # Process each camera in the project
            for camera_id, camera_data in project.get("cameras", {}).items():
                # Process each position for this camera
                for position, position_data in camera_data.get(
                    "position_settings", {}
                ).items():
                    # Process each area that this camera position covers
                    for area_id in position_data.get("area_metadata", {}).keys():
                        # Create or update the area mapping
                        if area_id not in areas_dict:
                            areas_dict[area_id] = AreaMapping(
                                area_id=area_id, cameras=[]
                            )

                        # Add this camera position to the area
                        areas_dict[area_id].cameras.append(
                            CameraPosition(camera_id=camera_id, position=position)
                        )

            # Create the project mapping
            project_mappings[project_id] = ProjectMapping(
                project_id=project_id, areas=areas_dict
            )

        return project_mappings
