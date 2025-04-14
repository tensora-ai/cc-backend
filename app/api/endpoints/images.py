from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import Response

from app.services.image_service import ImageService, get_image_service
from app.core.auth import validate_api_key

router = APIRouter(dependencies=[Depends(validate_api_key)])


@router.get("/{image_name}")
async def get_image(
    image_name: str = Path(..., description="Name of the image blob"),
    image_service: ImageService = Depends(get_image_service),
) -> Response:
    """
    Retrieve an image from blob storage.

    Args:
        image_name: Name of the image blob
        image_service: Service for image operations

    Returns:
        Binary response with the image data and appropriate content type
    """
    try:
        # Get the image bytes and content type
        image_bytes, content_type = await image_service.get_image(image_name)

        # Return the image as a binary response with the appropriate content type
        return Response(content=image_bytes, media_type=content_type)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log and wrap other exceptions
        print(f"Error retrieving image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while retrieving the image",
        )
