from azure.cosmos import ContainerProxy
from typing import List
from datetime import datetime

from app.models.prediction import CameraPosition, DATETIME_FORMAT, PredictionData


class PredictionRepository:
    """Repository for accessing prediction data from the database."""

    def __init__(self, predictions_container: ContainerProxy):
        self.container = predictions_container

    async def get_predictions_for_area(
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
            camera_positions: List of CameraPosition objects
            start_date: Start date for the query
            end_date: End date for the query

        Returns:
            List of PredictionData objects for each camera position
        """
        # Format dates for the query
        start_date_str = start_date.strftime(DATETIME_FORMAT)
        end_date_str = end_date.strftime(DATETIME_FORMAT)

        # Create empty result container
        prediction_data_list = []

        for camera in camera_positions:
            # Create the query
            query = f"""
                SELECT * FROM c 
                WHERE c.camera = '{camera.camera_id}' 
                AND c.position = '{camera.position}' 
                AND c.timestamp >= '{start_date_str}' 
                AND c.timestamp <= '{end_date_str}'
            """

            # Add to tasks list
            prediction_data = self._process_camera_query(
                query, project_id, area_id, camera.camera_id, camera.position
            )

            # Append the result to the list
            prediction_data_list.append(prediction_data)

        return prediction_data_list

    def _process_camera_query(
        self, query: str, project_id: str, area_id: str, camera_id: str, position: str
    ) -> PredictionData:
        """
        Process a query for a specific camera position.

        Args:
            query: The query to execute
            project_id: Project identifier (partition key)
            area_id: Area identifier for count lookup
            camera_id: Camera identifier
            position: Camera position

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
                # Extract timestamp and count for the requested area
                timestamp_str = prediction["timestamp"]
                # Convert string timestamp to datetime object
                timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)
                dates.append(timestamp)
                counts.append(prediction["counts"][area_id])
            except KeyError:
                # Skip predictions that don't have counts for this area
                continue

        # Return structured prediction data
        return PredictionData(
            dates=dates, counts=counts, camera_id=camera_id, position=position
        )
