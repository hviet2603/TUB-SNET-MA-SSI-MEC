from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import json
from datetime import date

from app.utils.models.web.base import SSIRequestWithContext
from app.utils.ssi.protocols.didexchange import didexchange_clear_connection
from app.utils.ssi.protocols.jsonld_issue_credential import (
    jsonld_issue_credential_issuer_send_offer,
    jsonld_issue_credential_issuer_handle_request,
)

from ..dependencies.dependencies import authenticate_request_with_VPExchange
from ..utils.vc_context import create_custom_vc_context_from_template
from ..env_config import WEB_PORT

router = APIRouter(prefix="/vc", tags=["vc"])

@router.get("/vc_context")
async def get_json_ld_context(request: Request):
    host = request.headers.get("host")

    content = create_custom_vc_context_from_template(f"http://{host}")

    return JSONResponse(content=json.loads(content), media_type="application/ld+json")

@router.post("/request_capability_delegation")
async def issue_capability_delegation_vc(
    req_wrapper: SSIRequestWithContext = Depends(authenticate_request_with_VPExchange)
):
    print("Authenticated, prepare to issue capability delegation VC")

    agent = req_wrapper.agent
    conn = req_wrapper.did_exchange.conn

    try:

        issuer = req_wrapper.agent
        issuer_agent_config = req_wrapper.agent_config

        # Issue credential
        requester_did = conn.their_public_did

        credential = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                f"http://{issuer_agent_config.host}:{WEB_PORT}/vc/vc_context",
            ],
            "type": ["VerifiableCredential", "CarCapabilityDelegation"],
            "issuer": issuer_agent_config.did,
            "issuanceDate": str(date.today()),
            "credentialSubject": {
                "type": "CarCapabilityDelegation",
                "id": requester_did,
                "car_twin_id": "car_twin_id_1",
                "car_id": "car_id_1",
                "capability_delegation": {
                    "position": ["read"],
                }
            },
        }

        cred_ex = await jsonld_issue_credential_issuer_send_offer(
            issuer,
            conn.connection_id,
            credential,
            options={"proofType": "Ed25519Signature2018"},
        )

        await jsonld_issue_credential_issuer_handle_request(issuer, cred_ex.cred_ex_id)

        return

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e

        print(e)

        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clear the connection
        await didexchange_clear_connection(agent, conn.connection_id)