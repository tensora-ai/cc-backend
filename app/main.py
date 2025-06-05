import logging

from fastapi import FastAPI
from app.api.routes import router
from dotenv import load_dotenv

load_dotenv()

# Suppress verbose logging from Azure Storage client
logging.getLogger(
    "azure.storage.common.storageclient"
).setLevel(logging.WARNING)

# Create FastAPI application with security dependencies
app = FastAPI(
    title="Tensora Count Backend",
    version="1.0",
    description="Backend for Tensora Count",
)

# Include routes
app.include_router(router, prefix="/api/v1")
