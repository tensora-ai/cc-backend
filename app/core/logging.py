import logging
from app.config import settings

logging.basicConfig(level=settings.LOG_LEVEL)


def get_logger(class_name: str):
    return logging.getLogger(class_name)
