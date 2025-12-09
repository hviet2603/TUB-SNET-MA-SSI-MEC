from fastapi import APIRouter, HTTPException

from app.app_digital_twin_car.env_config import get_agent_config
from app.app_digital_twin_car.utils.vc import request_vc
from acapy_controller import Controller
from app.utils.agent import create_agent_admin_url, create_public_agent_did

router = APIRouter(prefix="/app_migration", tags=["app_migration"])

""" Get the agent verkey when not yet published """

@router.get("/verkey")
async def get_agent_verkey():
    agent_config = get_agent_config()
    agent_admin_url = create_agent_admin_url(agent_config)
    agent = Controller(agent_admin_url)

    res = await agent.get("/wallet/did")

    for did_info in res["results"]:
        if did_info["method"] == "indy":
            return did_info["verkey"]

    return ""