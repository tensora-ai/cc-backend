from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from app.models.blob_storage import ContainerName
from app.services.blob_storage_service import (
    BlobStorageService,
    get_blob_storage_service,
)
from app.core.auth import validate_api_key

router = APIRouter(dependencies=[Depends(validate_api_key)])


@router.get("/{container}/{blob_path}")
async def get_blob(
    container: str,
    blob_path: str,
    blob_storage_service: BlobStorageService = Depends(get_blob_storage_service),
) -> Response:
    """
    Get a blob directly from the specified container and path.

    Args:
        container: Container name ('images' or 'predictions')
        blob_path: Full blob path/name
        blob_storage_service: Service for blob storage operations

    Returns:
        Blob content with appropriate content type
    """
    try:
        # Validate container name
        try:
            container_name = ContainerName(container)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid container name. Must be one of: {', '.join([c.value for c in ContainerName])}",
            )

        # Get the blob directly
        blob_bytes, content_type = await blob_storage_service.get_blob(
            container_name, blob_path
        )

        # Return the blob with the correct content type
        return Response(
            content=blob_bytes,
            media_type=content_type,
            headers={
                "Content-Disposition": f'inline; filename="{blob_path}"',
            },
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle other errors
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve blob: {str(e)}"
        )
