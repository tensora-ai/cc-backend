from typing import Optional, Tuple
from azure.storage.blob import BlobServiceClient
from fastapi import HTTPException


class ImageRepository:
    """Repository for accessing images from Azure Blob Storage."""

    def __init__(self, blob_service_client: BlobServiceClient, container_name: str):
        """
        Initialize the image repository.

        Args:
            blob_service_client: Azure Blob Service client
            container_name: Name of the container to access
        """
        self.blob_service_client = blob_service_client
        self.container_name = container_name
        self.container_client = self.blob_service_client.get_container_client(
            container_name
        )

    async def get_image(self, image_name: str) -> Optional[Tuple[bytes, str]]:
        """
        Retrieve an image blob as bytes with content type.

        Args:
            image_name: Name of the image to retrieve

        Returns:
            Tuple of (image bytes, content type) or None if not found

        Raises:
            HTTPException: For blob storage errors other than not found
        """
        try:
            # Get a client for the specific blob
            blob_client = self.container_client.get_blob_client(image_name)

            # Get properties to determine content type
            properties = blob_client.get_blob_properties()
            content_type = properties.content_settings.content_type

            # If content type is not set or is generic, infer from filename
            if not content_type or content_type == "application/octet-stream":
                content_type = self._infer_content_type(image_name)

            # Download the blob
            download_stream = blob_client.download_blob()
            blob_content = download_stream.readall()

            return blob_content, content_type

        except Exception as e:
            # Handle blob not found
            if "BlobNotFound" in str(e):
                return None

            # Re-raise other errors
            raise HTTPException(
                status_code=500, detail=f"Error retrieving image: {str(e)}"
            )

    def _infer_content_type(self, filename: str) -> str:
        """
        Infer content type from filename extension.

        Args:
            filename: Name of the file

        Returns:
            Inferred content type
        """
        # Check for common image types
        if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
            return "image/jpeg"
        elif filename.lower().endswith(".png"):
            return "image/png"
        elif filename.lower().endswith(".gif"):
            return "image/gif"
        elif filename.lower().endswith(".bmp"):
            return "image/bmp"
        elif filename.lower().endswith(".svg"):
            return "image/svg+xml"
        elif filename.lower().endswith(".tiff") or filename.lower().endswith(".tif"):
            return "image/tiff"
        elif filename.lower().endswith(".webp"):
            return "image/webp"

        # Default to generic binary if unknown
        return "application/octet-stream"
