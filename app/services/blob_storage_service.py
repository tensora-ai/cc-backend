from fastapi import HTTPException, Depends
from typing import Tuple
from azure.storage.blob import BlobServiceClient

from app.models.blob_storage import ContainerName
from app.repositories.blob_storage_repository import BlobStorageRepository
from app.core.blob_storage import get_blob_service_client
from app.core.logging import get_logger
import re


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
