from fastapi import APIRouter, HTTPException
import httpx
from ....env_config import TWIN_DRONE_WEB_URL
from ....utils.triggers import trigger_car_position_request
from app.utils.models.web.car_position import CarPositionRequestConnectionType

router = APIRouter(tags=["car_position"])

@router.post("/get_position_from_drone_twin")
async def get_position_from_drone_twin():
    try:

        car_position = await trigger_car_position_request(
            base_url=TWIN_DRONE_WEB_URL,
            connection_type=CarPositionRequestConnectionType.TWIN_CAR_TO_TWIN_DRONE
        )

        return car_position

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(status_code=500, detail=str(e))