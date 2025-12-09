from app.utils.agent import create_agent_admin_url, create_public_agent_did
from app.app_digital_twin_car.env_config import get_agent_config
from app.app_digital_twin_car.utils.vc import request_vc
from acapy_controller import Controller
import asyncio

async def publish_agent_on_new_verkey_registration(did: str, max_attempts=20):
    try:
        agent_config = get_agent_config()
        agent_admin_url = create_agent_admin_url(agent_config)
        agent = Controller(agent_admin_url)

        # Get the new verkey from wallet

        res = await agent.get("/wallet/did")
        new_verkey = None

        for did_info in res["results"]:
            if did_info["method"] == "indy":
                new_verkey = did_info["verkey"]

        if new_verkey == None:
            raise Exception(f"No valid verkey found for {did}!")

        # Check for new verkey on ledger

        attempts = 0

        while attempts < max_attempts:
            res = await agent.get(
                "/ledger/did-verkey",
                params={"did": did},
            )

            if res.get("verkey", "") == new_verkey:
                break

            attempts += 1
            await asyncio.sleep(1)

        if attempts >= max_attempts:
            raise Exception("The new verkey is not registered to ledger before timeout.")
        
        # New verkey is registered, publish the agent

        await create_public_agent_did(agent_config)

        request_vc_success = await request_vc()

        if request_vc_success:
            return
        else:
            raise Exception("VC request failed!")

    except Exception as e:
        print(e)
