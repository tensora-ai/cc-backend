# app/repositories/prediction_repository.py

from azure.cosmos import ContainerProxy
from typing import List
from datetime import datetime

from app.models.prediction import CameraPosition, DATETIME_FORMAT, PredictionData
from app.core.logging import get_logger


class PredictionRepository:
    """Repository for accessing prediction data from the database."""

    def __init__(self, predictions_container: ContainerProxy):
        self.container = predictions_container
        self.logger = get_logger(__name__)

    def get_predictions_for_area(
        self,
        project_id: str,
        area_id: str,
        camera_positions: List[CameraPosition],
        start_date: datetime,
        end_date: datetime,
    ) -> List[PredictionData]:
        """
        Retrieve predictions for all cameras in an area.

        Args:
            project_id: Project identifier (partition key)
            area_id: Area identifier for count lookup
            camera_positions: List of CameraPosition objects with masking information
            start_date: Start date for the query
            end_date: End date for the query

        Returns:
            List of PredictionData objects for each camera position
        """
        # Format dates for the query
        start_date_str = start_date.strftime(DATETIME_FORMAT)
        end_date_str = end_date.strftime(DATETIME_FORMAT)

        self.logger.info(
            f"Querying predictions from {start_date_str} to {end_date_str}",
        )

        # Create empty result container
        prediction_data_list = []

        for camera in camera_positions:
            # Create the query
            query = f"""
                SELECT * FROM c 
                WHERE c.project = '{project_id}' 
                AND c.camera = '{camera.camera_id}'
                AND c.position = '{camera.position}' 
                AND c.timestamp >= '{start_date_str}' 
                AND c.timestamp <= '{end_date_str}'
            """

            # Process the camera query with masking information
            prediction_data = self._process_camera_query(
                query,
                project_id,
                area_id,
                camera.camera_id,
                camera.position,
                camera.enable_masking,
            )

            # Append the result to the list
            prediction_data_list.append(prediction_data)

        return prediction_data_list

    def _process_camera_query(
        self,
        query: str,
        project_id: str,
        area_id: str,
        camera_id: str,
        position: str,
        enable_masking: bool,
    ) -> PredictionData:
        """
        Process a query for a specific camera position.

        Args:
            query: The query to execute
            project_id: Project identifier (partition key)
            area_id: Area identifier for count lookup
            camera_id: Camera identifier
            position: Camera position
            enable_masking: Whether masking is enabled for this camera configuration

        Returns:
            PredictionData with camera's dates and counts
        """
        # Create empty result containers
        dates = []
        counts = []

        # Execute the query
        query_results = self.container.query_items(
            query=query,
            partition_key=project_id,
            enable_cross_partition_query=False,  # Use partition key for efficiency
        )

        # Process each result
        for prediction in query_results:
            try:
                # Extract timestamp
                timestamp_str = prediction["timestamp"]

                # Convert string timestamp to datetime object retaining UTC timezone info
                timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)

                # Determine which count to use based on masking configuration
                if enable_masking:
                    # Use area-specific count when masking is enabled
                    if area_id not in prediction["counts"]:
                        self.logger.warning(
                            f"Masking enabled but area '{area_id}' not found in counts for "
                            f"camera {camera_id} at {timestamp_str}. Available keys: {list(prediction['counts'].keys())}"
                        )
                        continue  # Skip this prediction as it's missing expected area data

                    count = prediction["counts"][area_id]
                else:
                    # Use total count when masking is disabled
                    if "total" not in prediction["counts"]:
                        self.logger.warning(
                            f"Masking disabled but 'total' not found in counts for "
                            f"camera {camera_id} at {timestamp_str}. Available keys: {list(prediction['counts'].keys())}"
                        )
                        continue  # Skip this prediction as it's missing expected total data

                    count = prediction["counts"]["total"]

                # Only add to both arrays if we successfully extracted both timestamp and count
                dates.append(timestamp)
                counts.append(count)

            except KeyError as e:
                # Skip predictions that have structural issues
                self.logger.warning(
                    f"Skipping prediction due to missing key {e} for camera {camera_id} at position {position}"
                )
                continue
            except ValueError as e:
                # Skip predictions with invalid timestamp format
                self.logger.warning(
                    f"Skipping prediction due to invalid timestamp format: {e}"
                )
                continue

        # Log the results for debugging
        self.logger.info(
            f"Retrieved {len(counts)} predictions for camera {camera_id} at position {position} "
            f"(masking {'enabled' if enable_masking else 'disabled'})"
        )

        # Return structured prediction data
        return PredictionData(
            dates=dates, counts=counts, camera_id=camera_id, position=position
        )
