import httpx
import asyncio

from app.utils.agent import create_agent_admin_url
from app.utils.models.web.vc import VCIssuanceInitRequestModel
from ..env_config import AUTHORITY_WEB_URL, get_agent_config
from app.utils.ssi.protocols.didexchange import (
    didexchange_inviter_create_invitation,
    didexchange_inviter_handle_request,
)

from app.utils.ssi.protocols.jsonld_issue_credential import (
    jsonld_issue_credential_holder_receive_credential,
    jsonld_issue_credential_holder_send_request,
    jsonld_issue_credential_holder_wait_for_offer
)

from acapy_controller import Controller


async def request_vc():
    try:
        agent_config = get_agent_config()
        agent_admin_url = create_agent_admin_url(agent_config)

        holder = Controller(agent_admin_url)
        await holder.setup()

        invite = await didexchange_inviter_create_invitation(holder, agent_config.did)
        
        # Send the init request in the background
        client = httpx.AsyncClient(base_url=AUTHORITY_WEB_URL)
        
        init_request = VCIssuanceInitRequestModel(
            invite=invite.__dict__
        ).model_dump()

        asyncio.create_task(client.post(
            "/vc/issue",
            json=init_request,
        )) 

        # Handle DID exchange 
        conn = await didexchange_inviter_handle_request(holder, invite)

        # Process the received credential
        cred_ex = await jsonld_issue_credential_holder_wait_for_offer(holder, conn.connection_id)
        cred_ex = await jsonld_issue_credential_holder_send_request(holder, cred_ex.cred_ex_id)
        cred_ex = await jsonld_issue_credential_holder_receive_credential(holder, cred_ex.cred_ex_id)

    except Exception as e:
        print(e)
