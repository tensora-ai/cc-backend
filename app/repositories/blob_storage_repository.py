from typing import Optional, Tuple, List
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from fastapi import HTTPException

from app.models.blob_storage import ContainerName


class BlobStorageRepository:
    """Repository for accessing binaries from Azure Blob Storage."""

    def __init__(self, blob_service_client: BlobServiceClient):
        """
        Initialize the blob storage repository.

        Args:
            blob_service_client: Azure Blob Service client
        """
        self.blob_service_client = blob_service_client

    async def get_blob(
        self, container_name: ContainerName, blob_name: str
    ) -> Optional[Tuple[bytes, str]]:
        """
        Retrieve a blob as bytes with content type from the given container.

        Args:
            container_name: Name of the container to retrieve the blob from
            blob_name: Name of the blob to retrieve

        Returns:
            Tuple of (blob bytes, content type) or None if not found

        Raises:
            HTTPException: For blob storage errors other than not found
        """
        try:
            # Get the container client
            container_client = self.blob_service_client.get_container_client(
                container_name.value
            )

            # Get a client for the specific blob
            blob_client = container_client.get_blob_client(blob_name)

            # Get properties to determine content type
            properties = blob_client.get_blob_properties()
            content_type = properties.content_settings.content_type

            # If content type is not set or is generic, infer from filename
            if not content_type or content_type == "application/octet-stream":
                content_type = self._infer_content_type(blob_name)

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
                status_code=500,
                detail=f"Error retrieving blob from blob storage: {str(e)}",
            )

    async def list_blobs(
        self, container_name: ContainerName, prefix: str = None
    ) -> List[str]:
        """
        List blobs in a container with optional prefix filtering.

        Args:
            container_name: Container to list blobs from
            prefix: Optional prefix to filter blob names

        Returns:
            List of blob names

        Raises:
            HTTPException: For blob storage errors
        """
        try:
            # Get container client
            container_client = self.blob_service_client.get_container_client(
                container_name.value
            )

            # List blobs with optional prefix
            blob_items = container_client.list_blobs(name_starts_with=prefix)

            # Return list of blob names
            return [blob.name for blob in blob_items]

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error listing blobs in storage: {str(e)}"
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
        elif filename.lower().endswith(".json"):
            return "application/json"

        # Default to generic binary if unknown
        return "application/octet-stream"
