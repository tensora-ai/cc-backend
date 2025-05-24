import numpy as np
from fastapi import HTTPException, Depends
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from azure.cosmos import ContainerProxy

from app.core.database import get_container
from app.models.prediction import (
    AggregateTimeSeriesRequest,
    AggregateTimeSeriesResponse,
    ProjectMapping,
    AreaMapping,
    TimeSeriesPoint,
    CameraTimestamp,
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

    def _create_empty_time_series_response(self) -> AggregateTimeSeriesResponse:
        """
        Create an empty time series response.

        Returns:
            AggregateTimeSeriesResponse with empty time series
        """
        return AggregateTimeSeriesResponse(
            time_series=[],  # Empty list - no data points
            camera_timestamps=[],  # No camera timestamps since no data was used
        )

    def aggregate_time_series(
        self, project_id: str, area_id: str, request: AggregateTimeSeriesRequest
    ) -> AggregateTimeSeriesResponse:
        """
        Aggregate predictions for an area over time.

        This method:
        1. Validates the project and area exist
        2. Retrieves prediction data for all cameras in the area
        3. Checks data availability and handles empty/partial data cases
        4. Creates interpolation functions for each camera
        5. Calculates the sum across all cameras
        6. Applies optional smoothing
        7. Returns the aggregated time series with all actual timestamps from the database

        Args:
            project_id: Project identifier
            area_id: Area identifier
            request: Parameters for the aggregation

        Returns:
            Aggregated time series data (empty if no predictions found)

        Raises:
            HTTPException: If project/area not found or partial data scenario
        """
        # Step 1: Validate project and area exist
        area = self._get_area(project_id, area_id)

        if not area:
            # Provide helpful error message based on what's missing
            if project_id not in self.camera_mappings:
                raise HTTPException(
                    status_code=404, detail=f"Project '{project_id}' not found"
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Area '{area_id}' not found in project '{project_id}'",
                )

        # Step 2: Calculate time range
        end_dt = request.end_date
        start_dt = end_dt - timedelta(hours=request.lookback_hours)

        # Step 3: Get prediction data for all cameras in the area
        predictions = self.prediction_repo.get_predictions_for_area(
            project_id, area_id, area.cameras, start_dt, end_dt
        )

        # Step 4: Check data availability and handle different scenarios
        cameras_with_data = [pred for pred in predictions if pred.has_data]
        cameras_without_data = [pred for pred in predictions if not pred.has_data]

        # Case 1: No cameras have any data - return empty time series
        if len(cameras_with_data) == 0:
            return self._create_empty_time_series_response()

        # Case 2: Some cameras have data, others don't - this is problematic for aggregation
        if len(cameras_without_data) > 0:
            empty_camera_names = [
                f"{pred.camera_id}@{pred.position}" for pred in cameras_without_data
            ]
            raise HTTPException(
                status_code=422,
                detail=f"Partial prediction data found. Missing data for cameras: {', '.join(empty_camera_names)}. "
                f"Cannot aggregate when some cameras have data but others don't in the requested timespan.",
            )

        # Case 3: All cameras have data - proceed with normal processing

        # Step 5: Create camera timestamps for ALL available ACTUAL prediction timestamps
        # These are the real timestamps from the CosmosDB database, not synthetic ones
        camera_timestamps = []
        for pred in cameras_with_data:
            # Extract the actual timestamps from the database for this camera/position
            for timestamp in pred.dates:
                camera_timestamps.append(
                    CameraTimestamp(
                        camera_id=pred.camera_id,
                        position=pred.position,
                        timestamp=timestamp,  # This is the actual timestamp from CosmosDB
                    )
                )

        # Step 6: Create interpolation functions for each camera
        interpolation_result = PredictionProcessor.create_interpolation_functions(
            predictions, start_dt
        )

        # Step 7: Generate time grid from min to max date

        # Convert to UTC if timezone-aware, or assume UTC if naive
        def to_utc(dt: datetime) -> datetime:
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)

        min_date_utc: datetime = to_utc(interpolation_result.min_date)
        max_date_utc: datetime = to_utc(interpolation_result.max_date)
        start_dt_utc: datetime = to_utc(start_dt)

        # Create a uniform time grid for evaluation (30-second intervals)
        time_grid = np.linspace(
            (min_date_utc - start_dt_utc).total_seconds(),
            (max_date_utc - start_dt_utc).total_seconds(),
            num=int(request.lookback_hours * 120),
        )

        print(time_grid)

        # Step 8: Evaluate and sum all camera predictions on the time grid
        # Apply each interpolation function to the time grid and sum results
        sum_values = np.sum(
            [func(time_grid) for func in interpolation_result.interpolation_funcs],
            axis=0,
        )

        # Step 9: Apply moving average smoothing if requested
        smoothed_values = PredictionProcessor.apply_moving_average(
            sum_values, request.half_moving_avg_size
        )

        # Step 10: Generate time series points
        time_series = [
            TimeSeriesPoint(
                timestamp=start_dt + timedelta(seconds=t),
                value=max(0, int(v)),  # Ensure non-negative integer values
            )
            for t, v in zip(time_grid, smoothed_values)
        ]

        # Return the completed response with actual timestamps
        return AggregateTimeSeriesResponse(
            time_series=time_series, camera_timestamps=camera_timestamps
        )


def get_prediction_service(
    predictions_container: ContainerProxy = Depends(
        lambda: get_container("predictions")
    ),
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
    prediction_repository: ContainerProxy = PredictionRepository(predictions_container)
    project_repository: ProjectRepository = ProjectRepository(projects_container)

    # Load camera mappings from projects
    camera_mappings = project_repository.get_camera_mappings()

    # Create and return service
    return PredictionService(prediction_repository, camera_mappings)
