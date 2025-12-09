from acapy_controller import Controller
from acapy_controller.protocols import InvitationMessage
import httpx

from app.utils.models.web.vc import VC_TYPE
from app.utils.ssi.protocols.basicmessage import basicmessage_receive_message, basicmessage_send_message
from app.utils.web.vc import create_vp_definition
from ..env_config import AUTHORITY_WEB_URL, get_agent_config
from app.utils.agent import create_agent_admin_url
from app.utils.ssi.protocols.didexchange import (
    didexchange_inviter_create_invitation,
    didexchange_inviter_handle_request,
    didexchange_clear_connection,
)
from app.utils.ssi.protocols.jsonld_present_proof import (
    jsonld_present_proof_prover_send_proof,
    jsonld_present_proof_verifier_receive_presentation,
    jsonld_present_proof_verifier_send_request,
    jsonld_present_proof_verifier_verify_presentation,
)
import asyncio
from app.utils.models.web.application import (
    ApplicationConnectionType,
    AppMigrationInitRequestModel,
    ApplicationManifestModel,
    AppMigrationNewAppInfo,
)


async def _send_app_migration_request(
    base_url: str,
    invite: InvitationMessage,
    connection_type: ApplicationConnectionType,
):
    client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    init_request = AppMigrationInitRequestModel(
        invite=invite.__dict__,
        connection_type=connection_type,
    ).model_dump()

    return await client.post(
        "/apps/app_migration/initiate",
        json=init_request,
    )


async def trigger_application_migration(
    base_url: str, app_manifest: ApplicationManifestModel
) -> AppMigrationNewAppInfo:
    try:
        agent_config = get_agent_config()
        agent_admin_url = create_agent_admin_url(agent_config)

        agent = Controller(agent_admin_url)
        await agent.setup()

        invite = await didexchange_inviter_create_invitation(agent, agent_config.did)

        task = asyncio.create_task(
            _send_app_migration_request(
                base_url,
                invite,
                ApplicationConnectionType.TWIN_CAR_TO_EDGE,
            )
        )

        # Handle DID exchange
        conn = await didexchange_inviter_handle_request(agent, invite)

        # Handle VP exchange
        pres_ex = await jsonld_present_proof_prover_send_proof(
            agent, conn.connection_id
        )

        # Request proof from peer
        schema_uri = (
            f"{AUTHORITY_WEB_URL}/vc/vc_context#{VC_TYPE.EDGE.value}"
        )
        vp_definition = create_vp_definition(VC_TYPE.EDGE, schema_uri)

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

        # Do actual authorization work here
        if credential == None:
            raise Exception("The target is not an edge node!!!")
        
        # Send app manifest
        await basicmessage_send_message(
            agent, conn.connection_id, app_manifest.model_dump_json()
        )

        # Receive new app info
        app_info_json = await basicmessage_receive_message(agent, conn.connection_id, timeout=30)

        await task

        await didexchange_clear_connection(agent, conn.connection_id)

        app_info = AppMigrationNewAppInfo.model_validate_json(app_info_json)

        return app_info

    except Exception as e:
        print(e)
