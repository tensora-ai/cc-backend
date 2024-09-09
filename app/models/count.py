from pydantic import BaseModel
from datetime import datetime    
datetime_format = r"%Y-%m-%dT%H:%M:%SZ"


class Input(
    BaseModel,
    extra="forbid",
    json_encoders={datetime: lambda v: v.strftime(datetime_format)},
):

    project: str
    area: str
    end_date: str
    lookback_hours: float = 3
    half_moving_avg_size: int = 0

class PredictionSum(
    BaseModel,
    extra="forbid",
    json_encoders={datetime: lambda v: v.strftime(datetime_format)},
):

    timestamp: datetime
    prediction: int

class Output(
    BaseModel,
    extra="forbid",
):

    predictions_sum: list[PredictionSum]
    