from fastapi import HTTPException, Depends
from typing import Tuple, Optional
from azure.storage.blob import BlobServiceClient
from datetime import datetime

from app.models.blob_storage import ContainerName
from app.repositories.blob_storage_repository import BlobStorageRepository
from app.core.blob_storage import get_blob_service_client
from app.core.logging import get_logger


class BlobStorageService:
    """
    Service for handling blob retrieval operations.
    """

    def __init__(self, blob_storage_repository: BlobStorageRepository):
        """
        Initialize the blob storage service.

        Args:
            blob_storage_repository: Repository for accessing blobs from blob storage
        """
        self.blob_storage_repository = blob_storage_repository
        self.logger = get_logger(__name__)

    async def get_blob(
        self, container_name: ContainerName, blob_name: str
    ) -> Tuple[bytes, str]:
        """
        Retrieve a blob from blob storage as bytes with content type from a given container.

        Args:
            container_name: Name of the container to retrieve the blob from
            blob_name: Name of the blob to retrieve

        Returns:
            Tuple of (image bytes, content type)

        Raises:
            HTTPException: If the blob is not found
        """
        # Get the blob
        result = await self.blob_storage_repository.get_blob(container_name, blob_name)

        # Check if the blob was found
        if result is None:
            raise HTTPException(status_code=404, detail=f"Blob '{blob_name}' not found")

        # Return blob bytes and content type
        blob_bytes, content_type = result
        return blob_bytes, content_type

    def _parse_timestamp_from_blob_name(
        self, blob_name: str, suffix: str
    ) -> Optional[datetime]:
        """
        Extract timestamp from a blob name.

        Args:
            blob_name: Name of the blob
            suffix: Suffix for the blob name (to help identify timestamp part)

        Returns:
            Extracted timestamp or None if pattern doesn't match
        """
        try:
            # Remove suffix from the blob name
            name_without_suffix = blob_name.replace(suffix, "")

            # Split by hyphen to get parts
            parts = name_without_suffix.split("-")
            if len(parts) < 4:
                return None

            # The last part should contain the timestamp
            timestamp_part = parts[3]

            # Parse timestamp (format: YYYY_MM_DD-HH_MM_SS)
            timestamp = datetime.strptime(timestamp_part, "%Y_%m_%d-%H_%M_%S")
            return timestamp

        except (ValueError, IndexError):
            return None

    async def find_nearest_blob(
        self,
        container_name: ContainerName,
        prefix: str,
        target_timestamp: datetime,
        suffix: str,
    ) -> Tuple[str, datetime]:
        """
        Find the blob with the timestamp nearest to the target timestamp.

        Args:
            container_name: Container to search in
            prefix: Prefix for blob name filtering
            target_timestamp: Target timestamp to find nearest to
            suffix: Suffix for blob name filtering

        Returns:
            Tuple of (blob_name, blob_timestamp)

        Raises:
            HTTPException: If no matching blobs are found
        """
        # Get list of blobs from repository
        blob_names = await self.blob_storage_repository.list_blobs(
            container_name, prefix
        )

        # Filter blobs by suffix and extract timestamps
        matching_blobs = []

        for blob_name in blob_names:
            # Skip if it doesn't end with the required suffix
            if not blob_name.endswith(suffix):
                continue

            # Extract timestamp from blob name using the service method
            blob_timestamp = self._parse_timestamp_from_blob_name(blob_name, suffix)

            if blob_timestamp:
                matching_blobs.append((blob_name, blob_timestamp))

        # If no matching blobs were found, raise an error
        if not matching_blobs:
            raise HTTPException(
                status_code=404,
                detail=f"No matching blobs found for {prefix} with suffix {suffix}",
            )

        # Find the blob with the nearest timestamp
        nearest_blob = min(
            matching_blobs, key=lambda x: abs((x[1] - target_timestamp).total_seconds())
        )

        self.logger.info(
            f"Found nearest blob {nearest_blob[0]} for timestamp {target_timestamp}"
        )
        return nearest_blob


async def get_blob_storage_service(
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client),
):
    """
    Factory function to create the BlobStorageService with its dependencies.

    Args:
        blob_service_client: Azure Blob Service client

    Returns:
        Configured BlobStorageService instance
    """
    # Create repository
    repository = BlobStorageRepository(blob_service_client)

    # Create and return service
    return BlobStorageService(repository)
