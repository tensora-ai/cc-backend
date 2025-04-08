from azure.storage.blob import BlobServiceClient
import os


def get_blob_service_client() -> BlobServiceClient:
    """
    Get an Azure Blob Service client from the environment connection string.

    Returns:
        Azure Blob Service client
    """
    # Get connection string from environment variables
    connection_string = os.getenv("BLOB_CONNECTION")

    if not connection_string:
        raise ValueError("BLOB_CONNECTION environment variable is not set")

    # Create and return the client
    return BlobServiceClient.from_connection_string(connection_string)
