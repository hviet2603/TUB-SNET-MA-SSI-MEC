from fastapi import APIRouter, Depends, Request
from fastapi import HTTPException

from app.utils.ssi.protocols.didexchange import didexchange_clear_connection
from ..dependencies.dependencies import get_request_with_DIDExchange_context
from datetime import date

from app.utils.models.web.base import SSIRequestWithContext

from app.utils.ssi.protocols.jsonld_issue_credential import (
    jsonld_issue_credential_issuer_send_offer,
    jsonld_issue_credential_issuer_handle_request,
)

from ..utils.credentials import credentials
from ..utils.vc_context import create_custom_vc_context_from_template

from fastapi.responses import JSONResponse
import json

from ..env_config import WEB_PORT

router = APIRouter(prefix="/vc", tags=["verifiable_credentials"])


@router.get("/vc_context")
async def get_json_ld_context(request: Request):
    host = request.headers.get("host")

    content = create_custom_vc_context_from_template(f"http://{host}")

    return JSONResponse(content=json.loads(content), media_type="application/ld+json")


@router.post("/issue")
async def request_vc_issuance(
    req_wrapper: SSIRequestWithContext = Depends(get_request_with_DIDExchange_context),
):
    agent = req_wrapper.agent
    conn = req_wrapper.did_exchange.conn

    try:

        issuer = req_wrapper.agent
        issuer_agent_config = req_wrapper.agent_config

        # Issue credential
        requester_did = conn.their_public_did
        print(f"Requester: {requester_did}")
        credential_info = credentials[requester_did]

        credential = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                f"http://{issuer_agent_config.host}:{WEB_PORT}/vc/vc_context",
            ],
            "type": ["VerifiableCredential"] + credential_info["type"],
            "issuer": issuer_agent_config.did,
            "issuanceDate": str(date.today()),
            "credentialSubject": {
                "type": credential_info["type"],
                "id": requester_did,
                **credential_info["creds"],
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