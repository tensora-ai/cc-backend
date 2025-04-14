from fastapi import APIRouter
from app.models.health import HealthCheckResponse

router = APIRouter()


@router.get(response_model=HealthCheckResponse)
async def get_health_status() -> HealthCheckResponse:
    """Retrieve the health status of the service.

    Returns:
        HealthCheckResponse: Health status response.
    """

    # Simply return healthy for now
    # In the future, we can add checks for database connectivity, etc.
    return HealthCheckResponse(status="healthy", message="Service is running smoothly.")
