from azure.cosmos import ContainerProxy
from typing import Dict, Optional

from app.models.prediction import ProjectMapping, AreaMapping, CameraPosition


class ProjectRepository:
    """Repository for accessing project metadata and camera mappings."""

    def __init__(self, projects_container: ContainerProxy):
        self.container = projects_container

    async def get_camera_mappings(self) -> Dict[str, ProjectMapping]:
        """
        Extract project metadata and create structured mappings.

        Returns:
            Dict mapping project_id -> ProjectMapping objects
        """
        project_mappings = {}

        # Extract all project metadata with a single query
        async for project in self.container.query_items(
            query="SELECT c.id, c.cameras FROM c", enable_cross_partition_query=True
        ):
            project_id = project["id"]
            areas_dict = {}

            # Process each camera in the project
            for camera_id, camera_data in project["cameras"].items():
                # Process each position for this camera
                for position, position_data in camera_data.get(
                    "position_settings", {}
                ).items():
                    # Process each area that this camera position covers
                    for area_id in position_data["area_metadata"].keys():
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

    async def get_project(self, project_id: str) -> Optional[ProjectMapping]:
        """
        Get a project by ID.

        Args:
            project_id: The project identifier

        Returns:
            ProjectMapping if found, None otherwise
        """
        # Query for a specific project
        query = f"SELECT c.id, c.cameras FROM c WHERE c.id = @project_id"
        params = [{"name": "@project_id", "value": project_id}]

        # Execute the query
        projects = list(
            await self.container.query_items(
                query=query, parameters=params, enable_cross_partition_query=True
            ).to_list()
        )

        # No results found
        if not projects:
            return None

        # Process the project
        project = projects[0]
        project_id = project["id"]
        areas_dict = {}

        # Process cameras/positions/areas
        for camera_id, camera_data in project["cameras"].items():
            for position, position_data in camera_data.get(
                "position_settings", {}
            ).items():
                for area_id in position_data["area_metadata"].keys():
                    if area_id not in areas_dict:
                        areas_dict[area_id] = AreaMapping(area_id=area_id, cameras=[])

                    areas_dict[area_id].cameras.append(
                        CameraPosition(camera_id=camera_id, position=position)
                    )

        return ProjectMapping(project_id=project_id, areas=areas_dict)
