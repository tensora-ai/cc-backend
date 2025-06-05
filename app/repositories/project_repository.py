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

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects as raw dictionaries."""
        query = "SELECT * FROM c"
        items = self.container.query_items(
            query=query, enable_cross_partition_query=True
        )

        return list(items)

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a project by ID as a raw dictionary."""
        try:
            item = self.container.read_item(item=project_id, partition_key=project_id)
            return item
        except CosmosResourceNotFoundError:
            return None

    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project."""
        created_item = self.container.create_item(body=project_data)
        return created_item

    def update_project(
        self, project_id: str, project_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a project."""
        try:
            # Replace the entire document
            updated_item = self.container.replace_item(
                item=project_id, body=project_data
            )

            return updated_item
        except CosmosResourceNotFoundError:
            return None

    def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        try:
            self.container.delete_item(item=project_id, partition_key=project_id)
            return True
        except CosmosResourceNotFoundError:
            return False

    def get_camera_mappings(self) -> Dict[str, ProjectMapping]:
        """
        Extract project metadata and create structured mappings from the project structure.

        Returns:
            Dict mapping project_id -> ProjectMapping objects
        """
        project_mappings = {}

        # Extract all project data
        query = "SELECT * FROM c"
        query_results_paged = self.container.query_items(
            query=query, enable_cross_partition_query=True
        )

        # Convert to list by iterating
        query_results = list(query_results_paged)

        for project_data in query_results:
            project_id = project_data["id"]
            areas_dict = {}

            # Extract areas and camera configs from the project structure
            for area in project_data.get("areas", []):
                area_id = area.get("id")
                if not area_id:
                    continue  # Skip areas without ID

                # Initialize area mapping
                if area_id not in areas_dict:
                    areas_dict[area_id] = AreaMapping(area_id=area_id, cameras=[])

                # Process camera configurations for this area
                for camera_config in area.get("camera_configs", []):
                    camera_id = camera_config.get("camera_id")
                    position_data = camera_config.get("position", {})
                    position_name = position_data.get("name")

                    # Get masking information from camera config
                    enable_masking = camera_config.get("enable_masking", False)

                    if camera_id and position_name:
                        # Add this camera position to the area with masking info
                        areas_dict[area_id].cameras.append(
                            CameraPosition(
                                camera_id=camera_id,
                                position=position_name,
                                enable_masking=enable_masking,
                            )
                        )

            # Create the project mapping
            project_mappings[project_id] = ProjectMapping(
                project_id=project_id, areas=areas_dict
            )

        return project_mappings
