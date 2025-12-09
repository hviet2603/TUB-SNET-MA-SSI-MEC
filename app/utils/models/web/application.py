from enum import Enum
from pydantic import BaseModel
from typing import Dict, Any

class ApplicationConnectionType(str, Enum):
    EDGE_TO_EDGE = "edge_to_edge"
    EDGE_TO_TWIN_DRONE = "edge_to_twin_drone"
    EDGE_TO_TWIN_CAR = "edge_to_twin_car"
    TWIN_CAR_TO_EDGE = "twin_car_to_edge"
    TWIN_DRONE_TO_EDGE = "twin_drone_to_edge"

class ApplicationManifestModel(BaseModel):
    name: str
    image: str
    environment: Dict[str, str]
    ports: Dict[str, str]
    command: str

class AppMigrationInitRequestModel(BaseModel):
    type: str = "app_init_migration"
    invite: Dict[str, Any]
    connection_type: ApplicationConnectionType

class AppMigrationNewAppInfo(BaseModel):
    app_name: str
    new_verkey: str