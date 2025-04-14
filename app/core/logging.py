import logging
import os

from config import settings

logging.basicConfig(level=settings.LOG_LEVEL)


def get_logger(class_name: str):
    return logging.getLogger(class_name)
