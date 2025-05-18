from fastapi import APIRouter, Depends
from app.models.prediction import (
    AggregateTimeSeriesRequest,
    AggregateTimeSeriesResponse,
)
from app.services.prediction_service import PredictionService, get_prediction_service
from app.core.auth import validate_api_key

router = APIRouter(dependencies=[Depends(validate_api_key)])


@router.post("/aggregate", response_model=AggregateTimeSeriesResponse)
def aggregate_time_series(
    request: AggregateTimeSeriesRequest,
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> AggregateTimeSeriesResponse:
    """
    Aggregate predictions for a specific area over a time period.

    Calculates the sum of all camera predictions for the specified area,
    with optional moving average smoothing.

    Args:
        request: Parameters specifying project, area, time range, and smoothing
        prediction_service: Service for prediction calculations

    Returns:
        Aggregated predictions with timestamps
    """
    return prediction_service.aggregate_time_series(request)
