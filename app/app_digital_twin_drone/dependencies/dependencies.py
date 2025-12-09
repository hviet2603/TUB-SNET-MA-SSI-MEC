from ..env_config import get_agent_config
from app.utils.models.web.base import SSIRequestWithContext, SSIRequestModel
from app.utils.web.req_context_wrapper import wrap_request_with_DIDExchange_context
from fastapi import Depends, HTTPException
from app.utils.web.vc import VC_TYPE, create_vp_definition

from ..env_config import AUTHORITY_WEB_URL
from app.utils.models.web.application import ApplicationConnectionType
from app.utils.ssi.protocols.jsonld_present_proof import (
    jsonld_present_proof_prover_send_proof,
    jsonld_present_proof_verifier_send_request,
    jsonld_present_proof_verifier_receive_presentation,
    jsonld_present_proof_verifier_verify_presentation,
)

async def get_request_with_DIDExchange_context(
    req: SSIRequestModel,
) -> SSIRequestWithContext:
    agent_config = get_agent_config()

    return await wrap_request_with_DIDExchange_context(agent_config, req)


async def authenticate_request_with_VPExchange(
    wrapper=Depends(get_request_with_DIDExchange_context),
) -> SSIRequestWithContext:
    req = wrapper.req
    conn = wrapper.did_exchange.conn

    agent = wrapper.agent

    connection_type = req.connection_type

    vp_definition = None

    if connection_type == ApplicationConnectionType.EDGE_TO_TWIN_DRONE:
        schema_uri = (
            f"{AUTHORITY_WEB_URL}/vc/vc_context#{VC_TYPE.EDGE.value}"
        )
        vp_definition = create_vp_definition(VC_TYPE.EDGE, schema_uri)
        
    else:
        raise HTTPException(status_code=400, detail="Invalid connection type")

    # Send proof request
    pres_ex = await jsonld_present_proof_verifier_send_request(
        agent, conn.connection_id, vp_definition
    )

    # Wait for presentation
    pres_ex = await jsonld_present_proof_verifier_receive_presentation(
        agent, pres_ex.pres_ex_id
    )

    credential = pres_ex.by_format._extra["pres"]["dif"]["verifiableCredential"][0]

    # Verify presentation
    pres_ex = await jsonld_present_proof_verifier_verify_presentation(
        agent, pres_ex.pres_ex_id
    )

    # Do some authorization work
    if connection_type == ApplicationConnectionType.EDGE_TO_TWIN_DRONE:
        print(credential)
    else:
        raise HTTPException(status_code=400, detail="Invalid connection type")

    # Wait for peer request and send proof to peer
    pres_ex = await jsonld_present_proof_prover_send_proof(
        agent, conn.connection_id
    )

    return SSIRequestWithContext(
        req=req,
        agent=agent,
        agent_config=wrapper.agent_config,
        did_exchange=wrapper.did_exchange,
        credentials=[credential]
    )

