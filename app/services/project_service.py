from typing import List, Optional, Dict, Any

from fastapi import Depends

from app.models.project import Project, Camera, Area, CameraConfig, ProjectCreate
from app.repositories.project_repository import ProjectRepository
from app.core.database import get_container


class ProjectService:
    """Service for managing projects, cameras, areas and camera configurations."""

    def __init__(self, project_repository: ProjectRepository):
        self.repository = project_repository

    def list_projects(self) -> List[Project]:
        """List all projects."""
        items = self.repository.list_projects()
        return [Project.model_validate(item) for item in items]

    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        item = self.repository.get_project(project_id)
        if not item:
            return None
        return Project.model_validate(item)

    def create_project(self, project_data: ProjectCreate) -> Project:
        """Create a new project."""
        # Check if project already exists
        existing_project = self.get_project(project_data.id)
        if existing_project:
            raise ValueError(f"Project with ID {project_data.id} already exists")

        # Create new project with empty cameras and areas
        new_project = Project(id=project_data.id, name=project_data.name)

        # Create in database
        created_item = self.repository.create_project(new_project.model_dump())

        # Return the created project
        return Project.model_validate(created_item)

    def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        return self.repository.delete_project(project_id)

    # Camera operations
    def add_camera(self, project_id: str, camera_data: Camera) -> Project:
        """Add a camera to a project."""
        # Get the project
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")

        # Check if camera with same ID already exists
        if any(c.id == camera_data.id for c in project.cameras):
            raise ValueError(f"Camera with ID {camera_data.id} already exists")

        # Add camera to project
        project.cameras.append(camera_data)

        # Update project in database
        updated_item = self.repository.update_project(project_id, project.model_dump())

        # Return updated project
        return Project.model_validate(updated_item)

    def update_camera(
        self, project_id: str, camera_id: str, camera_data: Dict[str, Any]
    ) -> Project:
        """Update a camera in a project."""
        # Get the project
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")

        # Find the camera
        camera_index = None
        for i, camera in enumerate(project.cameras):
            if camera.id == camera_id:
                camera_index = i
                break

        if camera_index is None:
            raise ValueError(f"Camera with ID {camera_id} not found in project")

        # Update camera properties
        camera_dict = project.cameras[camera_index].model_dump()
        camera_dict.update(camera_data)

        # Preserve the camera ID
        camera_dict["id"] = camera_id

        # Replace the camera in the list
        project.cameras[camera_index] = Camera.model_validate(camera_dict)

        # Update project in database
        updated_item = self.repository.update_project(project_id, project.model_dump())

        # Return updated project
        return Project.model_validate(updated_item)

    def delete_camera(self, project_id: str, camera_id: str) -> Project:
        """Delete a camera from a project and remove any configurations using it."""
        # Get the project
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")

        # Check if camera exists
        if not any(c.id == camera_id for c in project.cameras):
            raise ValueError(f"Camera with ID {camera_id} not found in project")

        # Filter out the camera
        project.cameras = [c for c in project.cameras if c.id != camera_id]

        # Also remove any camera configurations using this camera
        for area in project.areas:
            area.camera_configs = [
                cc for cc in area.camera_configs if cc.camera_id != camera_id
            ]

        # Update project in database
        updated_item = self.repository.update_project(project_id, project.model_dump())

        # Return updated project
        return Project.model_validate(updated_item)

    # Area operations
    def add_area(self, project_id: str, area_data: Area) -> Project:
        """Add an area to a project."""
        # Get the project
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")

        # Check if area with same ID already exists
        if any(a.id == area_data.id for a in project.areas):
            raise ValueError(f"Area with ID {area_data.id} already exists")

        # Add area to project
        project.areas.append(area_data)

        # Update project in database
        updated_item = self.repository.update_project(project_id, project.model_dump())

        # Return updated project
        return Project.model_validate(updated_item)

    def update_area(
        self, project_id: str, area_id: str, area_data: Dict[str, Any]
    ) -> Project:
        """Update an area in a project."""
        # Get the project
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")

        # Find the area
        area_index = None
        for i, area in enumerate(project.areas):
            if area.id == area_id:
                area_index = i
                break

        if area_index is None:
            raise ValueError(f"Area with ID {area_id} not found in project")

        # Update area properties
        area_dict = project.areas[area_index].model_dump()
        area_dict.update(area_data)

        # Preserve the area ID
        area_dict["id"] = area_id

        # Replace the area in the list
        project.areas[area_index] = Area.model_validate(area_dict)

        # Update project in database
        updated_item = self.repository.update_project(project_id, project.model_dump())

        # Return updated project
        return Project.model_validate(updated_item)

    def delete_area(self, project_id: str, area_id: str) -> Project:
        """Delete an area from a project."""
        # Get the project
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")

        # Check if area exists
        if not any(a.id == area_id for a in project.areas):
            raise ValueError(f"Area with ID {area_id} not found in project")

        # Filter out the area
        project.areas = [a for a in project.areas if a.id != area_id]

        # Update project in database
        updated_item = self.repository.update_project(project_id, project.model_dump())

        # Return updated project
        return Project.model_validate(updated_item)

    # Camera configuration operations
    def add_camera_config(
        self, project_id: str, area_id: str, config_data: Dict[str, Any]
    ) -> Project:
        """Add a camera configuration to an area."""
        # Get the project
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")

        # Find the area
        area_index = None
        for i, area in enumerate(project.areas):
            if area.id == area_id:
                area_index = i
                break

        if area_index is None:
            raise ValueError(f"Area with ID {area_id} not found in project")

        # Check if camera config with same ID already exists
        if any(
            c.id == config_data.get("id")
            for c in project.areas[area_index].camera_configs
        ):
            raise ValueError(
                f"Camera Config with ID {config_data.get("id")} already exists in this area"
            )

        # Get camera ID from the config data
        camera_id = config_data.get("camera_id")
        if not camera_id:
            raise ValueError("Camera ID is required")

        # Check if camera exists in the project
        if not any(c.id == camera_id for c in project.cameras):
            raise ValueError(
                f"Camera with ID {camera_id} does not exist in the project"
            )

        # Get position from config data
        position = config_data.get("position")
        if not position or not isinstance(position, dict) or "name" not in position:
            raise ValueError("Valid position with name is required")

        position_name = position["name"]

        # Check if this camera position is already configured in this area
        if any(
            cc.camera_id == camera_id and cc.position.name == position_name
            for cc in project.areas[area_index].camera_configs
        ):
            raise ValueError(
                f"Camera {camera_id} is already configured in position {position_name}"
            )

        # Create camera config object
        camera_config = CameraConfig.model_validate(config_data)

        # Add config to area
        project.areas[area_index].camera_configs.append(camera_config)

        # Update project in database
        updated_item = self.repository.update_project(project_id, project.model_dump())

        # Return updated project
        return Project.model_validate(updated_item)

    def update_camera_config(
        self,
        project_id: str,
        area_id: str,
        camera_config_id: str,
        config_data: Dict[str, Any],
    ) -> Project:
        """Update a camera configuration in an area."""
        # Get the project
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")

        # Find the area
        area_index = None
        for i, area in enumerate(project.areas):
            if area.id == area_id:
                area_index = i
                break

        if area_index is None:
            raise ValueError(f"Area with ID {area_id} not found in project")

        # Find the camera config
        config_index = None
        for i, cc in enumerate(project.areas[area_index].camera_configs):
            if cc.id == camera_config_id:
                config_index = i
                break

        if config_index is None:
            raise ValueError(
                f"Camera configuration with ID {camera_config_id} not found in area {area_id}"
            )

        # Get the existing config
        camera_config = project.areas[area_index].camera_configs[config_index]

        # Update config properties
        config_dict = camera_config.model_dump()
        config_dict.update(config_data)

        # Preserve the camera config ID
        config_dict["id"] = camera_config_id

        # Replace the config in the list
        project.areas[area_index].camera_configs[config_index] = (
            CameraConfig.model_validate(config_dict)
        )

        # Update project in database
        updated_item = self.repository.update_project(project_id, project.model_dump())

        # Return updated project
        return Project.model_validate(updated_item)

    def delete_camera_config(
        self, project_id: str, area_id: str, camera_config_id: str
    ) -> Project:
        """Delete a camera configuration from an area."""
        # Get the project
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")

        # Find the area
        area_index = None
        for i, area in enumerate(project.areas):
            if area.id == area_id:
                area_index = i
                break

        if area_index is None:
            raise ValueError(f"Area {area_id} not found in project")

        # Check if the camera config exists
        if not any(
            cc.id == camera_config_id for cc in project.areas[area_index].camera_configs
        ):
            raise ValueError(
                f"Camera configuration {camera_config_id} not found in area {area_id}"
            )

        # Filter out the camera config
        project.areas[area_index].camera_configs = [
            cc
            for cc in project.areas[area_index].camera_configs
            if not (cc.id == camera_config_id)
        ]

        # Update project in database
        updated_item = self.repository.update_project(project_id, project.model_dump())

        # Return updated project
        return Project.model_validate(updated_item)


# Factory function for dependency injection
def get_project_service(
    project_repository: ProjectRepository = Depends(
        lambda: ProjectRepository(get_container("projects"))
    ),
):
    """Factory function to create a ProjectService instance."""
    return ProjectService(project_repository)
