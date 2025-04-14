import logging
import os

logging.basicConfig(level=os.getenv("LOG_LEVEL"))


def get_logger(class_name: str):
    return logging.getLogger(class_name)
