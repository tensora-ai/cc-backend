from fastapi import HTTPException
from fastapi import Security
from fastapi import status
from fastapi.security import APIKeyHeader

from app.config import settings

# Define the API key header
# This will be used to extract the API key from the request headers
# The header name is "X-API-KEY" and it is required
# If the header is not present, FastAPI automatically returns a 401 Unauthorized error
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)


async def validate_api_key(key: str = Security(api_key_header)) -> None:
    # Check if the API key is provided
    if key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized - API Key is wrong",
        )
