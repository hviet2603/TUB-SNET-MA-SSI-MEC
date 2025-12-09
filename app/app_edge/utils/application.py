from acapy_controller import Controller
from acapy_controller.protocols import InvitationMessage
import httpx

from app.utils.models.web.vc import VC_TYPE
from app.utils.web.vc import create_vp_definition
from ..env_config import (
    get_agent_config,
    EDGE_ALPHA_WEB_URL,
    EDGE_BETA_WEB_URL,
    AUTHORITY_WEB_URL,
)
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
from app.utils.ssi.protocols.basicmessage import (
    basicmessage_send_message,
    basicmessage_receive_message,
)
import asyncio
from app.utils.models.web.application import (
    ApplicationManifestModel,
    ApplicationConnectionType,
    AppMigrationInitRequestModel,
    AppMigrationNewAppInfo,
)

import docker


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

    res = await client.post(
        "/apps/app_migration/initiate",
        json=init_request,
    )

    return res


async def request_application_migration(
    app_manifest: ApplicationManifestModel,
) -> AppMigrationNewAppInfo:
    try:
        agent_config = get_agent_config()
        agent_admin_url = create_agent_admin_url(agent_config)

        agent = Controller(agent_admin_url)
        await agent.setup()

        invite = await didexchange_inviter_create_invitation(agent, agent_config.did)

        # Send the init request in the background
        other_edge_url = (
            EDGE_BETA_WEB_URL
            if agent_config.name == "edge_alpha"
            else EDGE_ALPHA_WEB_URL
        )

        task = asyncio.create_task(
            _send_app_migration_request(
                other_edge_url,
                invite,
                ApplicationConnectionType.EDGE_TO_EDGE,
            )
        )

        # Handle DID exchange
        conn = await didexchange_inviter_handle_request(agent, invite)

        # Send proof
        pres_ex = await jsonld_present_proof_prover_send_proof(
            agent, conn.connection_id
        )

        # Request proof from peer
        schema_uri = f"{AUTHORITY_WEB_URL}/vc/vc_context#{VC_TYPE.EDGE.value}"
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
        # raise e


async def get_new_app_verkey(base_url: str) -> str:
    client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    try:
        # Wait until the API server is ready
        attempts = 0

        while attempts < 30:
            try:
                res = await client.get("/")
                if res.status_code == 200:
                    break

            except Exception as e:
                print("New app API server is not responding, try again...")

            attempts += 1
            await asyncio.sleep(2)

        if attempts == 10:
            raise Exception("New app API server is not responding")

        # Get the new verkey

        res = await client.get("/apps/app_migration/verkey")

        return res.json()

    except Exception as e:
        print(e)


async def schedule_app_shutdown_on_new_verkey_registration(
    app_name: str, app_did: str, new_verkey: str, max_attempts: int = 20
):
    try:
        agent_config = get_agent_config()
        agent_admin_url = create_agent_admin_url(agent_config)

        agent = Controller(agent_admin_url)
        await agent.setup()

        # Check if the new verkey is registered

        attempts = 0

        while attempts < max_attempts:
            res = await agent.get(
                "/ledger/did-verkey",
                params={"did": app_did},
            )

            if res.get("verkey", "") == new_verkey:
                break

            attempts += 1
            await asyncio.sleep(1)

        if attempts >= max_attempts:
            raise Exception(
                "The new verkey is not registered to ledger before timeout."
            )

        # Shut down the old app

        print(f"Prepare to remove app {app_name}")

        docker_client = docker.from_env()
        container = docker_client.containers.get(app_name)

        if container.status == "running":
            container.stop()

        container.remove()

        print(f"Container {app_name} stopped and removed.")

    except Exception as e:
        print(e)
