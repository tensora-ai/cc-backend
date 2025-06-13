import aiohttp
from typing import Optional

from app.config import settings
from app.core.logging import get_logger


class PredictionBackendClient:
    """Client for communicating with the prediction backend for cache clearing purposes."""

    def __init__(self):
        """
        Initialize the PredictionBackendClient.
        """
        self.base_url = settings.PREDICT_BACKEND_BASE_URL
        self.api_key = settings.PREDICT_BACKEND_API_KEY
        self.logger = get_logger(__name__)

    async def clear_cache(self) -> bool:
        """
        Clear the cache in the prediction backend.

        Returns:
            True if cache was cleared successfully, False otherwise
        """
        try:
            url = f"{self.base_url}/admin/clear-cache"
            params = {"key": self.api_key}

            self.logger.info(f"Clearing cache in prediction backend at {url}")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        self.logger.info(
                            "Successfully cleared cache in prediction backend"
                        )
                        return True
                    else:
                        response_text = await response.text()
                        self.logger.warning(
                            f"Failed to clear cache in prediction backend. "
                            f"Status: {response.status}, Response: {response_text}"
                        )
                        return False

        except aiohttp.ClientTimeout:
            self.logger.error("Timeout while clearing cache in prediction backend")
            return False
        except aiohttp.ClientError as e:
            self.logger.error(
                f"Client error while clearing cache in prediction backend: {str(e)}"
            )
            return False
        except Exception as e:
            self.logger.error(
                f"Unexpected error while clearing cache in prediction backend: {str(e)}"
            )
            return False

    async def get_cache_stats(self) -> Optional[dict]:
        """
        Get cache statistics from the prediction backend.

        Returns:
            Cache statistics dict if successful, None otherwise
        """
        try:
            url = f"{self.base_url}/admin/cache-stats"
            params = {"key": self.api_key}

            self.logger.debug(f"Getting cache stats from prediction backend at {url}")

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        stats = await response.json()
                        self.logger.debug(
                            "Successfully retrieved cache stats from prediction backend"
                        )
                        return stats
                    else:
                        response_text = await response.text()
                        self.logger.warning(
                            f"Failed to get cache stats from prediction backend. "
                            f"Status: {response.status}, Response: {response_text}"
                        )
                        return None

        except aiohttp.ClientTimeout:
            self.logger.error(
                "Timeout while getting cache stats from prediction backend"
            )
            return None
        except aiohttp.ClientError as e:
            self.logger.error(
                f"Client error while getting cache stats from prediction backend: {str(e)}"
            )
            return None
        except Exception as e:
            self.logger.error(
                f"Unexpected error while getting cache stats from prediction backend: {str(e)}"
            )
            return None


def get_prediction_backend_client() -> PredictionBackendClient:
    """
    Factory function to create a PredictionBackendClient instance.

    Returns:
        Configured PredictionBackendClient instance
    """
    return PredictionBackendClient()
