from fastapi import APIRouter, HTTPException

from ....env_config import get_agent_config, CAR_WEB_URL
from ....utils.triggers import trigger_capability_delegation_request
from .....utils.models.web.capability_delegation import CapabilityDelegationRequestModel

router = APIRouter(prefix="/request_capability_delegation", tags=["request_capability_delegation"])

""" Send initiate app migration request to source edge from digital twin car app """

@router.post("/")
async def app_migration():
    try:
        
        await trigger_capability_delegation_request(
            base_url=CAR_WEB_URL
        )

        return

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e

        print(e)
        raise HTTPException(status_code=500, detail=str(e))
