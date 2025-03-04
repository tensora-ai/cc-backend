import os
from azure.cosmos.aio import CosmosClient, ContainerProxy
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.services.count_addition_service import CountAdditionService

app_resources = {}


async def get_camera_areas(database_client: ContainerProxy) -> list:
    # Extract all project metadata
    project_metadata = []
    async for item in database_client.query_items(
        query="SELECT c.id, c.cameras FROM c"
    ):
        project_metadata.append(item)

    area_cps = {}

    # Loop through all projects
    for project in project_metadata:
        id = project["id"]
        area_cps[id] = {}

        # Loop through all cameras in project
        for cam, cam_data in project["cameras"].items():
            # Loop through all positions of one camera
            for pos, pos_data in cam_data.get("position_settings", {}).items():
                # Loop through all areas of one position
                for area_key in pos_data["area_metadata"].keys():
                    area_cps[id].setdefault(area_key, []).append((cam, pos))

    return area_cps


@asynccontextmanager
async def lifespan(app: FastAPI):
    database_client = CosmosClient(
        url=os.getenv("COSMOS_DB_ENDPOINT"),
        credential=os.getenv("COSMOS_DB_PRIMARY_KEY"),
    ).get_database_client(os.getenv("COSMOS_DB_DATABASE_NAME"))

    app_resources["area_cps"] = await get_camera_areas(
        database_client.get_container_client("projects")
    )
    app_resources["count_add_service"] = CountAdditionService(
        database_client.get_container_client("predictions")
    )

    yield

    app_resources.clear()
