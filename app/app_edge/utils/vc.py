import httpx
import asyncio
import time

from app.utils.agent import create_agent_admin_url
from app.utils.models.web.vc import VCIssuanceInitRequestModel
from ..env_config import AUTHORITY_WEB_URL, get_agent_config
from app.utils.ssi.protocols.didexchange import (
    didexchange_inviter_create_invitation,
    didexchange_inviter_handle_request,
    didexchange_clear_connection
)

from app.utils.ssi.protocols.jsonld_issue_credential import (
    jsonld_issue_credential_holder_receive_credential,
    jsonld_issue_credential_holder_send_request,
    jsonld_issue_credential_holder_wait_for_offer,
)

from acapy_controller import Controller
from acapy_controller.protocols import InvitationMessage

from app.utils.logger import get_logger

metric_logger = get_logger()

async def _send_request_vc_init_request(base_url: str, invite: InvitationMessage):
    client = httpx.AsyncClient(base_url=base_url)

    init_request = VCIssuanceInitRequestModel(invite=invite.__dict__).model_dump()

    return await client.post(
        "/vc/issue",
        json=init_request,
    )


async def request_vc() -> bool:
    try:
        agent_config = get_agent_config()
        agent_admin_url = create_agent_admin_url(agent_config)

        holder = Controller(agent_admin_url)
        await holder.setup()

        res = await holder.get("/vc/credentials")
        if len(res["results"]) > 0:
            print("VC already exists, skip requesting new VC")
            return

        invite = await didexchange_inviter_create_invitation(holder, agent_config.did)

        # Send the init request in the background
        task = asyncio.create_task(
            _send_request_vc_init_request(AUTHORITY_WEB_URL, invite)
        )

        did_exchange_start = time.perf_counter()
        # Handle DID exchange
        conn = await didexchange_inviter_handle_request(holder, invite)
        did_exchange_end = time.perf_counter()
        metric_logger.info(f"[Request VC] DID exchange completed in {did_exchange_end - did_exchange_start} seconds")

        # Process the received credential
        vc_exchange_start = time.perf_counter()
        cred_ex = await jsonld_issue_credential_holder_wait_for_offer(
            holder, conn.connection_id
        )
        cred_ex = await jsonld_issue_credential_holder_send_request(
            holder, cred_ex.cred_ex_id
        )
        cred_ex = await jsonld_issue_credential_holder_receive_credential(
            holder, cred_ex.cred_ex_id
        )
        vc_exchange_end = time.perf_counter()
        metric_logger.info(f"[Request VC] VC exchange completed in {vc_exchange_end - vc_exchange_start} seconds")

        request_vc_res = await task

        await didexchange_clear_connection(holder, conn.connection_id)

        return True

    except Exception as e:
        print(e)

        return False
