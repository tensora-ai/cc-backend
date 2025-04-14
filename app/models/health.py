from datetime import datetime
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """
    Health check response model.
    """

    status: str
    message: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(datetime.timezone.utc)
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "Service is running smoothly.",
                "timestamp": "2023-10-01T12:00:00Z",
            }
        }
