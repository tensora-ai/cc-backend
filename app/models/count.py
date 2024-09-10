from pydantic import BaseModel, field_validator
from datetime import datetime

datetime_format = r"%Y-%m-%dT%H:%M:%SZ"


class AddCountsInput(
    BaseModel,
    extra="forbid",
    json_encoders={datetime: lambda v: v.strftime(datetime_format)},
):

    project: str
    area: str
    end_date: str
    lookback_hours: float = 3
    half_moving_avg_size: int = 0

    @field_validator("lookback_hours")
    def check_lookback_hours(cls, value):
        if value <= 0:
            raise ValueError("lookback_hours must be greater than 0")
        else:
            return value

    @field_validator("half_moving_avg_size")
    def check_half_moving_avg_size(cls, value):
        if value < 0:
            raise ValueError(
                "half_moving_avg_size must be greater or equal to 0"
            )
        else:
            return value


class PredictionSum(
    BaseModel,
    extra="forbid",
    json_encoders={datetime: lambda v: v.strftime(datetime_format)},
):

    timestamp: datetime
    prediction: int


class AddCountsOutput(
    BaseModel,
    extra="forbid",
):

    predictions_sum: list[PredictionSum]
