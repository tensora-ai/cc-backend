from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Callable

# Standard datetime format for the API
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class CameraPosition(BaseModel):
    """Represents a camera at a specific position."""

    camera_id: str = Field(..., description="Unique identifier for the camera")
    position: str = Field(..., description="Position setting name for the camera")

    def __str__(self) -> str:
        return f"{self.camera_id}@{self.position}"


class CameraTimestamp(BaseModel):
    """Timestamp information for a specific camera/position combination."""

    camera_id: str = Field(..., description="Camera identifier")
    position: str = Field(..., description="Position identifier")
    timestamp: datetime = Field(..., description="Timestamp of the prediction")

    def get_blob_prefix(self, project_id: str) -> str:
        """Generate blob prefix for this camera timestamp."""
        date_str = self.timestamp.strftime("%Y_%m_%d-%H_%M_%S")
        return f"{project_id}-{self.camera_id}-{self.position}-{date_str}"


class AreaMapping(BaseModel):
    """Mapping of an area to its cameras and positions."""

    area_id: str = Field(..., description="Unique identifier of the area")
    cameras: List[CameraPosition] = Field(
        default_factory=list, description="Cameras covering this area"
    )

    def __str__(self) -> str:
        return f"Area '{self.area_id}' with {len(self.cameras)} cameras"


class ProjectMapping(BaseModel):
    """Mapping of a project to its areas and their camera positions."""

    project_id: str = Field(..., description="Unique identifier of the project")
    areas: Dict[str, AreaMapping] = Field(
        default_factory=dict, description="Areas in this project"
    )

    def get_area(self, area_id: str) -> Optional[AreaMapping]:
        """Get an area by ID or None if it doesn't exist."""
        return self.areas.get(area_id)

    def __str__(self) -> str:
        return f"Project '{self.project_id}' with {len(self.areas)} areas"


class PredictionData(BaseModel):
    """Raw prediction data for a camera position."""

    dates: List[datetime] = Field(..., description="List of dates for the predictions")
    counts: List[int] = Field(
        ..., description="Corresponding count values for each date"
    )
    camera_id: str = Field(..., description="Camera identifier")
    position: str = Field(..., description="Camera position")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.strftime(DATETIME_FORMAT)}

    @property
    def has_data(self) -> bool:
        """Check if this prediction has any data points."""
        return len(self.dates) > 0

    @property
    def latest_date(self) -> datetime:
        """Get the datetime of the latest prediction."""
        if not self.has_data:
            raise ValueError("No prediction data available")
        return self.dates[-1]


class InterpolationResult(BaseModel):
    """Result of the interpolation process for all cameras."""

    interpolation_funcs: List[Callable] = Field(
        ..., description="Interpolation functions for each camera"
    )
    min_date: datetime = Field(..., description="Earliest date across all predictions")
    max_date: datetime = Field(..., description="Latest date across all predictions")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.strftime(DATETIME_FORMAT)}


class AggregateTimeSeriesRequest(BaseModel):
    """Request model for aggregating time series data."""

    end_date: datetime = Field(..., description="End date for the time series")
    lookback_hours: float = (
        Field(
            3.0,
            description="Number of hours to look back from the end date",
            gt=0,  # Must be greater than 0
        ),
    )
    half_moving_avg_size: int = Field(
        0,
        description="Half size of the moving average window (0 = no smoothing)",
        ge=0,  # Must be greater than or equal to 0
    )

    class Config:
        json_encoders = {datetime: lambda v: v.strftime(DATETIME_FORMAT)}
        json_schema_extra = {
            "example": {
                "end_date": "2025-03-05T10:00:00Z",
                "lookback_hours": 3.0,
                "half_moving_avg_size": 2,
            }
        }


class TimeSeriesPoint(BaseModel):
    """A single data point in a time series."""

    timestamp: datetime = Field(..., description="Timestamp of the data point")
    value: int = Field(..., description="Value at the given timestamp", ge=0)

    class Config:
        json_encoders = {datetime: lambda v: v.strftime(DATETIME_FORMAT)}


class AggregateTimeSeriesResponse(BaseModel):
    """Response model for aggregated time series data."""

    time_series: List[TimeSeriesPoint] = Field(
        ..., description="List of time series data points"
    )
    camera_timestamps: List[CameraTimestamp] = Field(
        default_factory=list,
        description="All available timestamps for each camera/position within the requested time range",
    )

    class Config:
        json_encoders = {datetime: lambda v: v.strftime(DATETIME_FORMAT)}
        json_schema_extra = {
            "example": {
                "time_series": [
                    {"timestamp": "2025-01-01T12:00:00Z", "value": 42},
                    {"timestamp": "2025-01-01T12:05:00Z", "value": 45},
                ],
                "camera_timestamps": [
                    {
                        "camera_id": "camera1",
                        "position": "position1",
                        "timestamp": "2025-01-01T12:00:00Z",
                    },
                    {
                        "camera_id": "camera1",
                        "position": "position1",
                        "timestamp": "2025-01-01T12:05:00Z",
                    },
                    {
                        "camera_id": "camera2",
                        "position": "position1",
                        "timestamp": "2025-01-01T12:00:00Z",
                    },
                ],
            }
        }


type DensityData = List[List[float]]
