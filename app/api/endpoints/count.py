from fastapi import APIRouter, Depends
from app.models.count import *
from app.services.count_addition_service import CountAdditionService, get_count_addition_service
from app.core.logging import get_logger
from app.resources import app_resources

router = APIRouter()

logger = get_logger(__name__)

@router.post("/", response_model=Output)
async def create_prediction_sum(input: Input, service: CountAdditionService = Depends(get_count_addition_service)) -> Output:
    """
    Erstellt eine Prediction Sum für ein Bestimmtes Intervall.

    Args:
        input (Input): Die Input Daten für die Prediction Sum.

    Returns:
        Output: Die Antwort mit der PredictionSum Liste.
    """
    return await service.get_prediction_sum(input, app_resources["area_cps"])


