from fastapi import Depends
from typing import Optional

from app.client.prediction_backend_client import (
    PredictionBackendClient,
    get_prediction_backend_client,
)
from app.core.logging import get_logger


class CacheService:
    """Service for managing cache operations across services."""

    def __init__(self, prediction_backend_client: PredictionBackendClient):
        """
        Initialize the cache service.

        Args:
            prediction_backend_client: Client for Prediction Backend service communication
        """
        self.prediction_backend_client = prediction_backend_client
        self.logger = get_logger(__name__)

    async def clear_project_cache(self, project_id: str, operation: str) -> bool:
        """
        Clear project-related cache after a configuration change.

        Args:
            project_id: ID of the project that was modified
            operation: Description of the operation performed (for logging)

        Returns:
            True if cache clearing was successful, False otherwise
        """
        self.logger.info(
            f"Clearing project cache for project '{project_id}' after operation: {operation}"
        )

        success = await self.prediction_backend_client.clear_cache()

        if success:
            self.logger.info(
                f"Successfully cleared cache for project '{project_id}' after {operation}"
            )
        else:
            self.logger.warning(
                f"Failed to clear cache for project '{project_id}' after {operation}. "
                f"Cache may be stale until next update."
            )

        return success

    async def get_cache_stats(self) -> Optional[dict]:
        """
        Get cache statistics from all services.

        Returns:
            Cache statistics if available, None otherwise
        """
        return await self.prediction_backend_client.get_cache_stats()


def get_cache_service(
    prediction_backend_client: PredictionBackendClient = Depends(
        get_prediction_backend_client
    ),
) -> CacheService:
    """
    Factory function to create a CacheService instance.

    Args:
        prediction_backend_client: Client for Prediction Backend service

    Returns:
        Configured CacheService instance
    """
    return CacheService(prediction_backend_client)
