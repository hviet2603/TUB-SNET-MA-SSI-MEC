from acapy_controller import Controller
from acapy_controller.protocols import InvitationMessage
from app.utils.ssi.protocols.didexchange import (
    didexchange_invitee_handle_response,
    didexchange_invitee_accept_invitation,
)
from ..agent import create_agent_admin_url
from ..models.web.didexchange import DIDExchangeContextModel
from ..models.web.base import SSIRequestWithContext, SSIRequestModel

from ..agent import AgentConfig

async def wrap_request_with_DIDExchange_context(
    agent_config: AgentConfig, 
    req: SSIRequestModel
):
    agent_admin_url = create_agent_admin_url(agent_config)

    invite = InvitationMessage(**req.invite)

    agent = Controller(agent_admin_url)
    await agent.setup()

    conn = await didexchange_invitee_accept_invitation(agent, invite)
    conn = await didexchange_invitee_handle_response(agent, conn.connection_id)

    wrapper = SSIRequestWithContext(
        req=req,
        agent=agent,
        agent_config=agent_config,
        did_exchange=DIDExchangeContextModel(conn=conn)
    )

    return wrapper