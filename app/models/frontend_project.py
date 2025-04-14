from pydantic import BaseModel
from typing import Dict, List


class CameraId(BaseModel):
    name: str
    position: str
    use_heatmap: bool


class Area(BaseModel):
    name: str
    half_moving_avg_size: int
    camera_ids: List[CameraId]


class GetFrontendProjectResponse(BaseModel):
    id: str
    name: str
    areas: List[Area]

    class Config:
        # Example for OpenAPI documentation
        json_schema_extra = {
            "example": {
                "id": "eventcore-demo",
                "name": "eventCORE Demo",
                "areas": [
                    {
                        "name": "Area 1",
                        "half_moving_avg_size": 10,
                        "camera_ids": [
                            {
                                "name": "Camera 1",
                                "position": "left",
                                "use_heatmap": True,
                            },
                            {
                                "name": "Camera 2",
                                "position": "right",
                                "use_heatmap": False,
                            },
                        ],
                    },
                    {
                        "name": "Area 2",
                        "half_moving_avg_size": 20,
                        "camera_ids": [
                            {
                                "name": "Camera 3",
                                "position": "front",
                                "use_heatmap": True,
                            },
                        ],
                    },
                ],
            }
        }
