from fastapi import APIRouter, Depends, HTTPException, Response

from app.models.prediction import (
    AggregateTimeSeriesRequest,
    AggregateTimeSeriesResponse,
)
from app.models.project import (
    Project,
    ProjectCreate,
    ProjectList,
    Camera,
    CameraCreate,
    CameraUpdate,
    Area,
    AreaCreate,
    AreaUpdate,
    CameraConfigCreate,
    CameraConfigUpdate,
)
from app.services.prediction_service import PredictionService, get_prediction_service
from app.services.project_service import ProjectService, get_project_service
from app.core.auth import validate_api_key

router = APIRouter(dependencies=[Depends(validate_api_key)])


# Project endpoints
@router.get("", response_model=ProjectList)
def list_projects(
    service: ProjectService = Depends(get_project_service),
) -> ProjectList:
    """
    List all projects.
    """
    try:
        projects = service.list_projects()
        return ProjectList(projects=projects)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list projects: {str(e)}"
        )


@router.get("/{project_id}", response_model=Project)
def get_project(
    project_id: str, service: ProjectService = Depends(get_project_service)
) -> Project:
    """
    Get a project by ID.
    """
    try:
        project = service.get_project(project_id)
        if not project:
            raise HTTPException(
                status_code=404, detail=f"Project with ID {project_id} not found"
            )
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")


@router.post("", response_model=Project)
def create_project(
    project: ProjectCreate, service: ProjectService = Depends(get_project_service)
) -> Project:
    """
    Create a new project.
    """
    try:
        created_project = service.create_project(project)
        return created_project
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create project: {str(e)}"
        )


@router.delete("/{project_id}", response_model=bool)
def delete_project(
    project_id: str, service: ProjectService = Depends(get_project_service)
) -> bool:
    """
    Delete a project.
    """
    try:
        success = service.delete_project(project_id)
        if not success:
            raise HTTPException(
                status_code=404, detail=f"Project with ID {project_id} not found"
            )
        return True
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete project: {str(e)}"
        )


# Camera endpoints
@router.post("/{project_id}/cameras", response_model=Project)
def add_camera(
    project_id: str,
    camera: CameraCreate,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    """
    Add a camera to a project.
    """
    try:
        # Convert to Camera model
        camera_model = Camera(**camera.model_dump())
        updated_project = service.add_camera(project_id, camera_model)
        return updated_project
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add camera: {str(e)}")


@router.put("/{project_id}/cameras/{camera_id}", response_model=Project)
def update_camera(
    project_id: str,
    camera_id: str,
    camera: CameraUpdate,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    """
    Update a camera in a project.
    """
    try:
        updated_project = service.update_camera(
            project_id, camera_id, camera.model_dump()
        )
        return updated_project
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update camera: {str(e)}"
        )


@router.delete("/{project_id}/cameras/{camera_id}", response_model=Project)
def delete_camera(
    project_id: str,
    camera_id: str,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    """
    Delete a camera from a project.
    """
    try:
        updated_project = service.delete_camera(project_id, camera_id)
        return updated_project
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete camera: {str(e)}"
        )


# Area endpoints
@router.post("/{project_id}/areas", response_model=Project)
def add_area(
    project_id: str,
    area: AreaCreate,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    """
    Add an area to a project.
    """
    try:
        # Convert to Area model
        area_model = Area(id=area.id, name=area.name)
        updated_project = service.add_area(project_id, area_model)
        return updated_project
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add area: {str(e)}")


@router.put("/{project_id}/areas/{area_id}", response_model=Project)
def update_area(
    project_id: str,
    area_id: str,
    area: AreaUpdate,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    """
    Update an area in a project.
    """
    try:
        updated_project = service.update_area(project_id, area_id, area.model_dump())
        return updated_project
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update area: {str(e)}")


@router.delete("/{project_id}/areas/{area_id}", response_model=Project)
def delete_area(
    project_id: str,
    area_id: str,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    """
    Delete an area from a project.
    """
    try:
        updated_project = service.delete_area(project_id, area_id)
        return updated_project
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete area: {str(e)}")


# Camera configuration endpoints
@router.post("/{project_id}/areas/{area_id}/camera-configs", response_model=Project)
def add_camera_config(
    project_id: str,
    area_id: str,
    config: CameraConfigCreate,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    """
    Add a camera configuration to an area.
    """
    try:
        updated_project = service.add_camera_config(
            project_id, area_id, config.model_dump()
        )
        return updated_project
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to add camera configuration: {str(e)}"
        )


@router.put(
    "/{project_id}/areas/{area_id}/camera-configs/{camera_config_id}",
    response_model=Project,
)
def update_camera_config(
    project_id: str,
    area_id: str,
    camera_config_id: str,
    config: CameraConfigUpdate,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    """
    Update a camera configuration in an area.
    """
    try:
        updated_project = service.update_camera_config(
            project_id, area_id, camera_config_id, config.model_dump()
        )
        return updated_project
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update camera configuration: {str(e)}"
        )


@router.delete(
    "/{project_id}/areas/{area_id}/camera-configs/{camera_config_id}",
    response_model=Project,
)
def delete_camera_config(
    project_id: str,
    area_id: str,
    camera_config_id: str,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    """
    Delete a camera configuration from an area.
    """
    try:
        updated_project = service.delete_camera_config(
            project_id, area_id, camera_config_id
        )
        return updated_project
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete camera configuration: {str(e)}"
        )


@router.post(
    "/{project_id}/areas/{area_id}/predictions/aggregate",
    response_model=AggregateTimeSeriesResponse,
)
def aggregate_time_series(
    project_id: str,
    area_id: str,
    request: AggregateTimeSeriesRequest,
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> AggregateTimeSeriesResponse:
    """
    Aggregate predictions for a specific area over a time period.

    Calculates the sum of all camera predictions for the specified area,
    with optional moving average smoothing.

    Args:
        project_id: Project identifier
        area_id: Area identifier
        request: Parameters specifying time range, and smoothing
        prediction_service: Service for prediction calculations

    Returns:
        Aggregated predictions with timestamps
    """
    return prediction_service.aggregate_time_series(project_id, area_id, request)
