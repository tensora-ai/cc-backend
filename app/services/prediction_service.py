import numpy as np
from fastapi import HTTPException, Depends
from datetime import timedelta
from typing import Dict, Optional

from app.core.database import get_container
from app.models.prediction import (
    AggregateTimeSeriesRequest,
    AggregateTimeSeriesResponse,
    ProjectMapping,
    AreaMapping,
    TimeSeriesPoint,
)
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.project_repository import ProjectRepository
from app.services.prediction_processor import PredictionProcessor


class PredictionService:
    """
    Service for aggregating and processing prediction data.
    This service handles the business logic for time series aggregation.
    """

    def __init__(
        self,
        prediction_repository: PredictionRepository,
        camera_mappings: Dict[str, ProjectMapping],
    ):
        """
        Initialize the prediction service.

        Args:
            prediction_repository: Repository for accessing prediction data
            camera_mappings: Mapping of projects to their areas and cameras
        """
        self.prediction_repo = prediction_repository
        self.camera_mappings = camera_mappings

        # Create processor for time series calculations
        self.processor = PredictionProcessor()

    def _get_area(self, project_id: str, area_id: str) -> Optional[AreaMapping]:
        """
        Get area mapping by project and area ID.

        Args:
            project_id: Project identifier
            area_id: Area identifier

        Returns:
            AreaMapping if found, None otherwise
        """
        project = self.camera_mappings.get(project_id)
        if not project:
            return None

        return project.get_area(area_id)

    async def aggregate_time_series(
        self, request: AggregateTimeSeriesRequest
    ) -> AggregateTimeSeriesResponse:
        """
        Aggregate predictions for an area over time.

        This method:
        1. Validates the project and area exist
        2. Retrieves prediction data for all cameras in the area
        3. Creates interpolation functions for each camera
        4. Calculates the sum across all cameras
        5. Applies optional smoothing
        6. Returns the aggregated time series

        Args:
            request: Parameters for the aggregation

        Returns:
            Aggregated time series data

        Raises:
            HTTPException: If project/area not found or data is insufficient
        """
        # Step 1: Validate project and area exist
        area = self._get_area(request.project, request.area)

        if not area:
            # Provide helpful error message based on what's missing
            if request.project not in self.camera_mappings:
                raise HTTPException(
                    status_code=404, detail=f"Project '{request.project}' not found"
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Area '{request.area}' not found in project '{request.project}'",
                )

        # Step 2: Calculate time range
        end_dt = request.end_date
        start_dt = end_dt - timedelta(hours=request.lookback_hours)

        # Step 3: Get prediction data for all cameras in the area
        predictions = await self.prediction_repo.get_predictions_for_area(
            request.project, request.area, area.cameras, start_dt, end_dt
        )

        # Step 4: Create interpolation functions for each camera
        interpolation_result = PredictionProcessor.create_interpolation_functions(
            predictions, start_dt, request.project
        )

        # Step 5: Generate time grid from min to max date
        # Create a uniform time grid for evaluation (30-second intervals)
        time_grid = np.linspace(
            (interpolation_result.min_date - start_dt).total_seconds(),
            (interpolation_result.max_date - start_dt).total_seconds(),
            num=int(request.lookback_hours * 120),
        )

        # Step 6: Evaluate and sum all camera predictions on the time grid
        # Apply each interpolation function to the time grid and sum results
        sum_values = np.sum(
            [func(time_grid) for func in interpolation_result.interpolation_funcs],
            axis=0,
        )

        # Step 7: Apply moving average smoothing if requested
        smoothed_values = PredictionProcessor.apply_moving_average(
            sum_values, request.half_moving_avg_size
        )

        # Step 8: Generate time series points
        time_series = [
            TimeSeriesPoint(
                timestamp=start_dt + timedelta(seconds=t),
                value=max(0, int(v)),  # Ensure non-negative integer values
            )
            for t, v in zip(time_grid, smoothed_values)
        ]

        # Return the completed response
        return AggregateTimeSeriesResponse(
            time_series=time_series, source_ids=interpolation_result.source_ids
        )


async def get_prediction_service(
    predictions_container=Depends(lambda: get_container("predictions")),
    projects_container=Depends(lambda: get_container("projects")),
) -> PredictionService:
    """
    Factory function to create the PredictionService with its dependencies.

    Args:
        predictions_container: Container for prediction data
        projects_container: Container for project metadata

    Returns:
        Configured PredictionService instance
    """
    # Create repositories
    prediction_repository = PredictionRepository(predictions_container)
    project_repository = ProjectRepository(projects_container)

    # Load camera mappings from projects
    camera_mappings = await project_repository.get_camera_mappings()

    # Create and return service
    return PredictionService(prediction_repository, camera_mappings)
