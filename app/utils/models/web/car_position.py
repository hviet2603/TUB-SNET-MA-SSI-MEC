from pydantic import BaseModel
from typing import Dict, Any
from enum import Enum

class CarPositionRequestConnectionType(str, Enum):
    TWIN_CAR_TO_TWIN_DRONE = "twin_car_to_twin_drone"
    CAR_TO_TWIN_DRONE = "car_to_twin_drone"

class CarPositionRequestModel(BaseModel):
    type: str = "car_position"
    invite: Dict[str, Any]
    connection_type: CarPositionRequestConnectionType

class CarPosition(BaseModel):
    x: float
    y: float
    z: float
