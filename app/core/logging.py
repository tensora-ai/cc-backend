import logging
import os

logging.basicConfig(level=os.getenv("COSMOS_DB_ENDPOINT"))

def get_logger(class_name: str):
    return logging.getLogger(class_name)