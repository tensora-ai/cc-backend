from fastapi import FastAPI, Depends
from fastapi.security.api_key import APIKeyHeader
from app.api.routes import router
from dotenv import load_dotenv

load_dotenv()

# Create FastAPI application with security dependencies
app = FastAPI(
    title="Tensora Count Backend",
    version="1.0",
    description="Backend for Tensora Count",
)

# Include routes
app.include_router(router, prefix="/api/v1")
