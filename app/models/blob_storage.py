from enum import Enum


class ContainerName(Enum):
    """Enum for container names in Azure Blob Storage."""

    IMAGES = "images"
    DENSITY = "predictions"
