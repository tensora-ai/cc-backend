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
    areas: Dict[str, Area]

    class Config:
        # Example for OpenAPI documentation
        schema_extra = {
            "example": {
                "id": "eventcore-demo",
                "name": "eventCORE Demo",
                "areas": {
                    "test_area": {
                        "name": "Test Area",
                        "half_moving_avg_size": 10,
                        "camera_ids": [
                            {
                                "name": "Camera 1",
                                "position": "front",
                                "use_heatmap": True,
                            },
                            {
                                "name": "Camera 2",
                                "position": "back",
                                "use_heatmap": False,
                            },
                        ],
                    }
                },
            }
        }
