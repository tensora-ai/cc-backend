from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from app.api.routes import router
from dotenv import load_dotenv

import os

load_dotenv()

api_key_header = APIKeyHeader(name="api-key", auto_error=True)


def validate_api_key(api_key: str = Security(api_key_header)):
    """Validate the API key from the request header."""
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key


# Create FastAPI application with security dependencies
app = FastAPI(
    title="Tensora Count Backend",
    version="1.0",
    description="Backend for Tensora Count",
    dependencies=[Depends(validate_api_key)],
)

# Include routes
app.include_router(router, prefix="/api/v1")
