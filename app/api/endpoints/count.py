from fastapi import APIRouter
from app.models.count import AddCountsInput, AddCountsOutput
from app.resources import app_resources

router = APIRouter()


@router.post("/sum_predictions", response_model=AddCountsOutput)
async def create_prediction_sum(
    input: AddCountsInput,
) -> AddCountsOutput:
    """
    Erstellt eine Prediction Sum für ein gegebenes Intervall.

    Args:
        input (AddCountsOutput): Die Input Daten für die Prediction Sum.

    Returns:
        AddCountsOutput: Die Antwort mit der PredictionSum Liste.
    """
    return await app_resources["count_add_service"](
        input, app_resources["area_cps"][input.project]
    )
