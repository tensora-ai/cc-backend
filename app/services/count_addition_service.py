from datetime import datetime, timedelta
import numpy as np
from scipy.interpolate import CubicSpline
from azure.cosmos import DatabaseProxy
from fastapi import Depends
from app.core.logging import get_logger
from app.models.count import *
from app.core.database import get_database
from app.core.logging import get_logger


async def get_count_addition_service(database_client: DatabaseProxy = Depends(get_database)):
    return CountAdditionService(database_client) 

class CountAdditionService:
    
    def __init__(self, database_client: DatabaseProxy):
        self.profile_container_client_projects = database_client.get_container_client("projects")
        self.profile_container_client_predictions = database_client.get_container_client("predictions")
        self.logger = get_logger(__name__)

# ------------------------------------------------------------------------------
    
    async def _calculate_interpolation(self, area_cps : list, input : Input) -> tuple[list,list,list]:
    # Interpolate
        interpolation_funcs = []

        # Just for plotting
        all_dates = []
        all_counts = []
        for cam, pos, area in area_cps:
            if area == input.area:
                predictions = self.profile_container_client_predictions.query_items(
                    query=f"SELECT c.timestamp, c.counts FROM c WHERE c.camera = '{cam}' AND c.position = '{pos}' AND c.timestamp >= '{self.start_date}' AND c.timestamp <= '{input.end_date}'",
                    partition_key=input.project
                )
                
                dates, counts = map(list, zip(*[(p["timestamp"], p["counts"][input.area]) for p in predictions]))

                counts = np.array(counts)

                # To calculate a reasonable variable for the x-axis
                rescaled_dates = np.array([datetime.strptime(d, datetime_format) for d in dates]) - self.start_dt
                rescaled_dates = np.array([d.total_seconds() for d in rescaled_dates])

                interpolation_funcs.append(CubicSpline(rescaled_dates, counts))

                # Just for plotting
                all_dates.append(rescaled_dates)
                all_counts.append(counts)
        return interpolation_funcs, all_dates, all_counts
    
    async def _calculate_moving_avarage(self, input:Input, sum) -> list :
        window_size = 2 * input.half_moving_avg_size + 1


        # concetaneta to ensure same size after calculating average
        sum_avg = np.convolve(np.concatenate([sum[:input.half_moving_avg_size], sum, sum[-input.half_moving_avg_size:]]),
                            np.ones(window_size),
                            mode="valid"
                            ) / window_size
        
        return sum_avg
# ------------------------------------------------------------------------------
    async def get_prediction_sum(self, input: Input, area_cps:list) -> Output:
        self.end_dt = datetime.strptime(input.end_date, datetime_format)
        self.start_dt = self.end_dt - timedelta(hours=input.lookback_hours)
        self.start_date = self.start_dt.strftime(datetime_format)
        interpolation_funcs, all_dates, all_counts = await self._calculate_interpolation(area_cps, input)

        pd_grid = np.linspace(0, (self.end_dt - self.start_dt).total_seconds(), num=int(input.lookback_hours*120))
        sum = np.array([f(pd_grid) for f in interpolation_funcs]).sum(axis=0)
        new_times = [self.start_dt + timedelta(seconds=s) for s in pd_grid]

        moving_average = await self._calculate_moving_avarage(input, sum)

        prediction_sums = [
            PredictionSum(timestamp=dt, prediction=int(pred)) for dt, pred in zip(new_times, moving_average)
        ]
        return Output(predictions_sum=prediction_sums)