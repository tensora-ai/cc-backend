import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from app._paths import ROOT_PATH

env_file_path = ROOT_PATH / ".env"

if env_file_path.exists():
    load_dotenv(env_file_path)


class Settings(BaseSettings):
    """Settings for the application."""

    # Azure CosmosDB settings
    COSMOS_DB_ENDPOINT: str
    COSMOS_DB_PRIMARY_KEY: str
    COSMOS_DB_DATABASE_NAME: str

    # Azure BlobStorage settings
    AZURE_STORAGE_CONNECTION_STRING: str

    # Logging settings
    LOG_LEVEL: str = "INFO"

    # Security settings
    API_KEY: str

    # Prediction backend settings
    PREDICT_BACKEND_BASE_URL: str
    PREDICT_BACKEND_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=env_file_path if env_file_path.exists() else None,
        extra="forbid",
    )


# Instantiate settings once. pydantic-settings handles loading from
# environment variables and the specified .env file.
settings = Settings(
    COSMOS_DB_ENDPOINT=os.getenv("COSMOS_DB_ENDPOINT"),
    COSMOS_DB_PRIMARY_KEY=os.getenv("COSMOS_DB_PRIMARY_KEY"),
    COSMOS_DB_DATABASE_NAME=os.getenv("COSMOS_DB_DATABASE_NAME"),
    AZURE_STORAGE_CONNECTION_STRING=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    LOG_LEVEL=os.getenv("LOG_LEVEL"),
    API_KEY=os.getenv("API_KEY"),
    PREDICT_BACKEND_BASE_URL=os.getenv("PREDICT_BACKEND_BASE_URL"),
    PREDICT_BACKEND_API_KEY=os.getenv("PREDICT_BACKEND_API_KEY"),
)
