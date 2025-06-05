import numpy as np
from scipy.interpolate import interp1d
from typing import List
from datetime import datetime, timedelta

from app.core.logging import get_logger
from app.models.prediction import (
    TimeSeriesPoint,
    PredictionData,
    InterpolationResult,
)
from app.utils.time_utils import to_utc


class PredictionProcessor:
    """Utility class for processing prediction data."""

    @staticmethod
    def create_interpolation_functions(
        predictions: List[PredictionData], start_dt: datetime
    ) -> InterpolationResult:
        """
        Create interpolation functions for each camera's predictions.

        Note: This method assumes all predictions have data. Empty data scenarios
        should be handled before calling this method.

        Args:
            predictions: List of prediction data for all cameras in an area
            start_dt: Start datetime for the time series
            project_id: Project identifier

        Returns:
            InterpolationResult: Object containing interpolation functions, min/max dates
        """

        # Create interpolation functions for each camera
        interpolation_funcs = []
        dates = []

        for pred in predictions:
            # Collect all dates for min/max calculation
            dates.extend(pred.dates)

            # Create interpolation function based on number of data points
            if len(pred.dates) == 1:
                # For a single data point, create a constant function
                interpolation_funcs.append(
                    lambda d, count=pred.counts[0]: np.full(len(d), count)
                )
            else:
                # Calculate seconds elapsed since start_dt for each date
                rescaled_dates = [
                    (to_utc(date) - to_utc(start_dt)).total_seconds()
                    for date in pred.dates
                ]

                # Create linear interpolation function
                interpolation_funcs.append(
                    interp1d(
                        np.array(rescaled_dates),
                        np.array(pred.counts),
                        kind="linear",
                        fill_value="extrapolate",
                    )
                )

        # Find min and max dates across all predictions
        min_date = min(dates)
        max_date = max(dates)

        return InterpolationResult(
            interpolation_funcs=interpolation_funcs,
            min_date=min_date,
            max_date=max_date,
        )

    @staticmethod
    def apply_moving_average(values: np.ndarray, half_window_size: int) -> np.ndarray:
        """
        Apply a moving average filter to a time series.

        Args:
            values: Array of values to smooth
            half_window_size: Half size of the averaging window
                              (0 means no smoothing)

        Returns:
            Smoothed array of values

        Notes:
            Uses edge padding to avoid boundary issues.
        """
        # If no smoothing requested, return the original values
        if half_window_size == 0:
            return values

        # Calculate full window size
        window_size = 2 * half_window_size + 1

        # Create a padded array to avoid edge effects
        # We pad with the first and last values to avoid introducing
        # artificial trends at the boundaries
        padded_values = np.concatenate(
            [
                np.full(half_window_size, values[0]),  # Pad start with first value
                values,  # Original data
                np.full(half_window_size, values[-1]),  # Pad end with last value
            ]
        )

        # Create a uniform filter window
        window = np.ones(window_size) / window_size

        # Apply convolution and return
        return np.convolve(padded_values, window, mode="valid")

    @staticmethod
    def generate_time_points(
        start_dt: datetime, time_grid: np.ndarray, values: np.ndarray
    ) -> List[TimeSeriesPoint]:
        """
        Generate TimeSeriesPoint objects from time grid and values.

        Args:
            start_dt: Base datetime for the time grid
            time_grid: Array of seconds since start_dt
            values: Array of values corresponding to each time point

        Returns:
            List of TimeSeriesPoint objects
        """
        return [
            TimeSeriesPoint(
                timestamp=start_dt + timedelta(seconds=t),
                value=max(0, int(v)),  # Ensure non-negative integers
            )
            for t, v in zip(time_grid, values)
        ]
