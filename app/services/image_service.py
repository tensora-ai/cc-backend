from fastapi import HTTPException, Depends
from typing import Tuple
from azure.storage.blob import BlobServiceClient

from app.repositories.image_repository import ImageRepository
from app.core.blob_storage import get_blob_service_client


async def get_image_repository(
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client),
):
    """
    Factory function to create a BlobRepository instance.

    Args:
        blob_service_client: Azure Blob Service client

    Returns:
        Configured BlobRepository instance
    """
    # Create repository for the images container
    container_name = "images"
    return ImageRepository(blob_service_client, container_name)


async def get_image_service(
    image_repository=Depends(get_image_repository),
):
    """
    Factory function to create the ImageService with its dependencies.

    Args:
        image_repository: Repository for accessing images from blob storage

    Returns:
        Configured ImageService instance
    """
    return ImageService(image_repository)


class ImageService:
    """
    Service for handling image retrieval operations.
    """

    def __init__(self, image_repository: ImageRepository):
        """
        Initialize the image service.

        Args:
            image_repository: Repository for accessing images from blob storage
        """
        self.image_repository = image_repository

    async def get_image(self, image_name: str) -> Tuple[bytes, str]:
        """
        Retrieve an image from blob storage as bytes with content type.

        Args:
            image_name: Name of the image blob to retrieve

        Returns:
            Tuple of (image bytes, content type)

        Raises:
            HTTPException: If the image is not found
        """
        # Get the image
        result = await self.image_repository.get_image(image_name)

        # Check if the image was found
        if result is None:
            raise HTTPException(
                status_code=404, detail=f"Image '{image_name}' not found"
            )

        # Return image bytes and content type
        image_bytes, content_type = result
        return image_bytes, content_type
