import numpy as np
import asyncio
from fastapi import HTTPException
from datetime import datetime, timedelta
from scipy.interpolate import interp1d
from azure.cosmos import ContainerProxy

from app.models.count import AddCountsInput, AddCountsOutput, PredictionSum

datetime_format = "%Y-%m-%dT%H:%M:%SZ"


# ------------------------------------------------------------------------------
class CountAdditionService:
    def __init__(self, database_client: ContainerProxy):
        self.db_client = database_client

    # ---------------------------------------------------------------------------
    async def __call__(
        self, input: AddCountsInput, area_cps: list
    ) -> AddCountsOutput:
        end_dt = datetime.strptime(input.end_date, datetime_format)
        start_dt = end_dt - timedelta(hours=input.lookback_hours)
        start_date_str = start_dt.strftime(datetime_format)

        # Interpolate predictions from all cameras
        interpolation_funcs, min_date, max_date = (
            await self._construct_interpolation_funcs(
                area_cps, input, start_dt, start_date_str
            )
        )

        # Evaluate sum of all cameras on equidistant grid between overall lowest
        # and highest date given in predictions from all cameras
        rescaled_dates_grid = np.linspace(
            (min_date - start_dt).total_seconds(),
            (max_date - start_dt).total_seconds(),
            num=int(input.lookback_hours * 120),
        )
        print(rescaled_dates_grid)

        sum = np.array(
            [f(rescaled_dates_grid) for f in interpolation_funcs]
        ).sum(axis=0)
        sum_mv = self._calculate_moving_avarage(input.half_moving_avg_size, sum)

        # Construct output
        dates_grid = [
            start_dt + timedelta(seconds=s) for s in rescaled_dates_grid
        ]
        result = [
            PredictionSum(timestamp=dt, prediction=max(0, int(pred)))
            for dt, pred in zip(dates_grid, sum_mv)
        ]
        return AddCountsOutput(predictions_sum=result)

    # --------------------------------------------------------------------------
    async def _construct_interpolation_funcs(
        self,
        area_cps: dict[str, list[tuple[str, str]]],
        input: AddCountsInput,
        start_dt: datetime,
        start_date_str: str,
    ) -> list[interp1d]:
        """Returns a list of interpolation functions for the predictions of each
        camera and position."""
        all_preds = await self._retrieve_all_predictions(
            area_cps[input.area], input, start_date_str
        )

        interpolation_funcs = []
        empty_cps = []
        for (dates, counts), cp in all_preds:
            if len(dates) == 0:
                empty_cps.append(cp)
                continue

            # To calculate a reasonable variable for the x-axis
            rescaled_dates = [
                (
                    datetime.strptime(d, datetime_format) - start_dt
                ).total_seconds()
                for d in dates
            ]

            interpolation_funcs.append(
                interp1d(
                    np.array(rescaled_dates),
                    np.array(counts),
                    kind="linear",
                    fill_value="extrapolate",
                )
            )

        if len(empty_cps) > 0:
            raise HTTPException(
                status_code=422,
                detail=f"No predictions found for cameras and positions {empty_cps}.",
            )

        min_date = datetime.strptime(
            min([all_preds[i][0][0][0] for i in range(len(all_preds))]),
            datetime_format,
        )
        max_date = datetime.strptime(
            max([all_preds[i][0][0][-1] for i in range(len(all_preds))]),
            datetime_format,
        )
        return interpolation_funcs, min_date, max_date

    # --------------------------------------------------------------------------
    async def _retrieve_all_predictions(
        self,
        cam_pos: list[tuple[str, str]],
        input: AddCountsInput,
        start_date_str: str,
    ) -> list[tuple[list[str], list[int]]]:
        """Returns a list of tuples with dates and counts for each camera and position."""
        all_preds = [
            self.db_client.query_items(
                query=f"SELECT * FROM c WHERE c.camera = '{cam}' AND c.position = '{pos}' AND c.timestamp >= '{start_date_str}' AND c.timestamp <= '{input.end_date}'",
                partition_key=input.project,
            )
            for cam, pos in cam_pos
        ]

        async def retrieve_dates_and_counts(predictions):
            camera_dates = []
            camera_counts = []
            async for p in predictions:
                camera_dates.append(p["timestamp"])
                camera_counts.append(p["counts"][input.area])

            return (camera_dates, camera_counts)

        return list(
            zip(
                await asyncio.gather(
                    *[
                        retrieve_dates_and_counts(predictions)
                        for predictions in all_preds
                    ]
                ),
                cam_pos,
            )
        )

    # --------------------------------------------------------------------------
    def _calculate_moving_avarage(
        self, half_moving_avg_size: int, sum: list[float]
    ) -> list[float]:
        if half_moving_avg_size == 0:
            return sum
        else:
            window_size = 2 * half_moving_avg_size + 1

            sum_avg = np.convolve(
                np.concatenate(
                    [
                        [sum[0]] * half_moving_avg_size,
                        sum,
                        [sum[-1]] * half_moving_avg_size,
                    ]
                ),  # To ensure reasonable values at the edges
                np.ones(window_size) / window_size,
                mode="valid",
            )

            return sum_avg
