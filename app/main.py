from fastapi import FastAPI
from app.api.routes import router
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from azure.cosmos import DatabaseProxy
from app.core.database import get_database
from app.resources import app_resources


load_dotenv()



async def _get_camera_areas(database_client : DatabaseProxy) -> list:
        
    # Extrahiere alle Kameras
    project_cams = list(database_client.query_items(
        query="SELECT c.cameras FROM c", 
        enable_cross_partition_query=True  
    ))

    area_cps = []

    # Durchlaufe die Ergebnisse
    for location in project_cams:
        cameras = location.get("cameras", {})
        
        # Iteriere über die Kameras
        for cam, cam_data in cameras.items():
            # Iteriere über die Positionseinstellungen der Kamera
            for pos, pos_data in cam_data.get("position_settings", {}).items():
                # Iteriere über die area_metadata und hole den Key (z.B. "faster")
                for area_key, area_data in pos_data.get("area_metadata", {}).items():
                    area_cps.append((cam, pos, area_key))
    return area_cps


@asynccontextmanager
async def lifespan(app: FastAPI):
    database_client = await get_database()
    profile_container_client_projects = database_client.get_container_client("projects")
    # Rufe die Funktion auf und speichere das Ergebnis in app_resources
    app_resources["area_cps"] = await _get_camera_areas(profile_container_client_projects)

    yield  # Applikation startet hiermit

    # Aufräumen, falls notwendig
    app_resources.clear()


app = FastAPI(
    title=os.getenv("PROJECT_NAME"),
    lifespan=lifespan
)
app.include_router(router, prefix=os.getenv("API_BASE_URL"))