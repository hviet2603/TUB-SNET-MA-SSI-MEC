from fastapi import HTTPException
from acapy_controller import Controller
from acapy_controller.protocols import InvitationMessage
import httpx
import time

from app.utils.models.web.vc import VC_TYPE
from app.utils.ssi.protocols.basicmessage import basicmessage_receive_message, basicmessage_send_message
from app.utils.ssi.protocols.jsonld_issue_credential import jsonld_issue_credential_holder_receive_credential, jsonld_issue_credential_holder_send_request, jsonld_issue_credential_holder_wait_for_offer
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

from app.utils.models.web.capability_delegation import CapabilityDelegationRequestModel
from app.utils.models.web.car_position import CarPositionRequestModel, CarPositionRequestConnectionType, CarPosition
from app.utils.logger import get_logger

metric_logger = get_logger()

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

async def _send_capability_delegation_request(
    base_url: str,
    invite: InvitationMessage,
):
    client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    init_request = CapabilityDelegationRequestModel(
        invite=invite.__dict__,
    ).model_dump()

    return await client.post(
        "/vc/request_capability_delegation",
        json=init_request,
    )


async def _send_car_position_request(
    base_url: str,
    invite: InvitationMessage,
    connection_type: CarPositionRequestConnectionType,
):
    client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    init_request = CarPositionRequestModel(
        invite=invite.__dict__,
        connection_type=connection_type,
    ).model_dump()

    return await client.post(
        "/car/get_position",
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
        did_exchange_start = time.perf_counter()
        conn = await didexchange_inviter_handle_request(agent, invite)
        did_exchange_end = time.perf_counter()
        metric_logger.info(f"[App Migration] DID exchange completed in {did_exchange_end - did_exchange_start} seconds")

        # Handle VP exchange
        vc_exchange_start = time.perf_counter()
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
        vc_exchange_end = time.perf_counter()
        metric_logger.info(f"[App Migration] VP exchange completed in {vc_exchange_end - vc_exchange_start} seconds")
        
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

async def trigger_capability_delegation_request(
    base_url: str
):
    try:

        agent_config = get_agent_config()
        agent_admin_url = create_agent_admin_url(agent_config)

        agent = Controller(agent_admin_url)
        await agent.setup()

        res = await agent.get("/vc/credentials")
        if len(res["results"]) > 1:
            print("Capability delegation VC already exists, skip requesting new VC")
            return

        invite = await didexchange_inviter_create_invitation(agent, agent_config.did)

        task = asyncio.create_task(
            _send_capability_delegation_request(
                base_url,
                invite,
            )
        )

        # Handle DID exchange
        conn = await didexchange_inviter_handle_request(agent, invite)

        # Prover sends proof of being the car twin
        pres_ex = await jsonld_present_proof_prover_send_proof(
            agent, conn.connection_id
        )

        # Request proof from peer
        schema_uri = (
            f"{AUTHORITY_WEB_URL}/vc/vc_context#{VC_TYPE.CAR.value}"
        )
        vp_definition = create_vp_definition(VC_TYPE.CAR, schema_uri)

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
            raise Exception("The target is not the car!!!")
        
        # Receive the capability delegation VC
        cred_ex = await jsonld_issue_credential_holder_wait_for_offer(
            agent, conn.connection_id
        )
        cred_ex = await jsonld_issue_credential_holder_send_request(
            agent, cred_ex.cred_ex_id
        )
        cred_ex = await jsonld_issue_credential_holder_receive_credential(
            agent, cred_ex.cred_ex_id
        )
    
        await didexchange_clear_connection(agent, conn.connection_id)

    except Exception as e:
        print(e)

async def trigger_car_position_request(
    base_url: str,
    connection_type: CarPositionRequestConnectionType,
) -> CarPosition:
    try:

        agent_config = get_agent_config()
        agent_admin_url = create_agent_admin_url(agent_config)

        agent = Controller(agent_admin_url)
        await agent.setup()

        invite = await didexchange_inviter_create_invitation(agent, agent_config.did)

        task = asyncio.create_task(
            _send_car_position_request(
                base_url,
                invite,
                connection_type,
            )
        )

        # Handle DID exchange
        did_exchange_start = time.perf_counter()
        conn = await didexchange_inviter_handle_request(agent, invite)
        did_exchange_end = time.perf_counter()
        metric_logger.info(f"[Car Position] DID exchange completed in {did_exchange_end - did_exchange_start} seconds")

        # Prover sends proof of being the car twin
        vc_exchange_start = time.perf_counter()
        pres_ex = await jsonld_present_proof_prover_send_proof(
            agent, conn.connection_id
        )

        # Request proof from peer
        schema_uri = (
            f"{AUTHORITY_WEB_URL}/vc/vc_context#{VC_TYPE.DRONE_TWIN.value}"
        )
        vp_definition = create_vp_definition(VC_TYPE.DRONE_TWIN, schema_uri)

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
        vc_exchange_end = time.perf_counter()
        metric_logger.info(f"[Car Position] VP exchange completed in {vc_exchange_end - vc_exchange_start} seconds")

        # Do actual authorization work here
        if credential == None:
            raise Exception("The target is not the drone twin!!!")
        
        try: 
            # Prover sends proof of possessing the capability delegation VC
            cap_vc_exchange_start = time.perf_counter()
            pres_ex = await jsonld_present_proof_prover_send_proof(
                agent, conn.connection_id
            )
            cap_vc_exchange_end = time.perf_counter()
            metric_logger.info(f"[Car Position] Capability delegation VP exchange completed in {cap_vc_exchange_end - cap_vc_exchange_start} seconds")
        
        except Exception as e:
            raise HTTPException(status_code=403, detail="The car twin does not have the capability delegation VC, access denied")

        # Receive car position info
        car_position_json = await basicmessage_receive_message(agent, conn.connection_id, timeout=30)
    
        await task
    
        await didexchange_clear_connection(agent, conn.connection_id)

        car_position = CarPosition.model_validate_json(car_position_json)

        return car_position

    except Exception as e:
        raise e