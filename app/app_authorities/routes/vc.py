from fastapi import APIRouter
from acapy_controller import Controller
from fastapi import HTTPException

from datetime import date

from app.utils.models.web.vc import VCIssuanceInitRequestModel
from app.utils.ssi.protocols.didexchange import (
    didexchange_invitee_handle_response,
    didexchange_invitee_accept_invitation,
)

from app.utils.ssi.protocols.jsonld_issue_credential import (
    jsonld_issue_credential_issuer_send_offer,
    jsonld_issue_credential_issuer_handle_request,
)

from acapy_controller.protocols import InvitationMessage

from ..env_config import get_agent_config
from app.utils.agent import create_agent_admin_url
from .data.credentials import credentials

from fastapi.responses import JSONResponse
from pathlib import Path
import json

from ..env_config import WEB_PORT

router = APIRouter(prefix="/vc", tags=["verifiable_credentials"])

@router.get("/vc_context")
async def get_json_ld_context():
    file_path = Path(__file__).parent / "data" / "context.jsonld" 

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return JSONResponse(
        content=data,
        media_type="application/ld+json"
    )

@router.post("/issue")
async def request_vc_issuance(init_request_info: VCIssuanceInitRequestModel):
    try:
        issuer_agent_config = get_agent_config()
        issuer_admin_url = create_agent_admin_url(issuer_agent_config)

        invite = InvitationMessage(**init_request_info.invite)

        issuer = Controller(issuer_admin_url)
        await issuer.setup()

        # Handle DID exchanges
        conn = await didexchange_invitee_accept_invitation(issuer, invite)
        conn = await didexchange_invitee_handle_response(issuer, conn.connection_id)

        # Issue credential
        requester_did = conn.their_public_did
        print(f"Requester: {requester_did}")
        credential_info = credentials[requester_did]

        credential = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                f"http://{issuer_agent_config.host}:{WEB_PORT}/vc/vc_context"
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
