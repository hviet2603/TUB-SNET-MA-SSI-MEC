from fastapi import APIRouter, Depends
import random

from app.utils.models.web.car_position import CarPositionRequestModel, CarPosition
from app.utils.ssi.protocols.basicmessage import basicmessage_send_message
from app.utils.ssi.protocols.didexchange import didexchange_clear_connection
from ...dependencies.dependencies import authenticate_request_with_VPExchange
from app.utils.models.web.base import SSIRequestWithContext

router = APIRouter(prefix="/car", tags=["car"])

@router.post("/get_position")
async def car_position(req_wrapper: SSIRequestWithContext = Depends(authenticate_request_with_VPExchange)):
    
    agent = req_wrapper.agent
    conn = req_wrapper.did_exchange.conn
    req: CarPositionRequestModel = req_wrapper.req
    agent_config = req_wrapper.agent_config

    print("Authenticated, send car position")

    try:
        car_position = CarPosition(
            x=round(random.uniform(1, 100), 2), 
            y=round(random.uniform(1, 100), 2), 
            z=round(random.uniform(1, 100), 2)
        )

        await basicmessage_send_message(
            agent,
            connection_id=conn.connection_id,
            content=car_position.model_dump_json(),
        )

        return car_position
    
    finally:
        # Clear the connection
        await didexchange_clear_connection(agent, conn.connection_id)