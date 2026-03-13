from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import time

from app.app_edge.utils.application import (
    get_new_app_verkey,
    request_application_migration,
    schedule_app_shutdown_on_new_verkey_registration,
)
from app.utils.ssi.protocols.basicmessage import (
    basicmessage_send_message,
    basicmessage_receive_message,
)
from ....dependencies.dependencies import authenticate_request_with_VPExchange
from app.utils.models.web.application import (
    AppMigrationInitRequestModel,
    AppMigrationNewAppInfo,
    ApplicationConnectionType,
    ApplicationManifestModel,
)
from app.utils.models.web.base import SSIRequestWithContext
from app.utils.ssi.protocols.didexchange import didexchange_clear_connection
from app.utils.logger import get_logger
import docker

router = APIRouter(prefix="/app_migration", tags=["app_migration"])

metrics_logger = get_logger()

""" Initiate the app migration process, must be called from either source edge or from digital twin apps """


@router.post("/initiate")
async def app_migration(
    background_tasks: BackgroundTasks,
    req_wrapper: SSIRequestWithContext = Depends(authenticate_request_with_VPExchange),
):

    print("Authenticated, prepare to migrate app")

    agent = req_wrapper.agent
    conn = req_wrapper.did_exchange.conn
    req: AppMigrationInitRequestModel = req_wrapper.req
    agent_config = req_wrapper.agent_config

    # Get app manifest
    app_manifest_json = await basicmessage_receive_message(
        agent, conn.connection_id, timeout=10
    )
    
    app_manifest = ApplicationManifestModel.model_validate_json(app_manifest_json)
    print(app_manifest)

    try:

        new_app_info: AppMigrationNewAppInfo = None

        # Do the actual migration work
        if req.connection_type == ApplicationConnectionType.EDGE_TO_EDGE:

            # Role: Destination Edge

            app_deployment_start = time.perf_counter()

            app_host = agent_config.host

            edge_app_name = (
                "ma-ssi-edge-alpha"
                if agent_config.name == "edge_alpha"
                else "ma-ssi-edge-beta"
            )

            # Step 1: Start the new container

            docker_client = docker.from_env()

            # Step 1.1: Extract the new host name

            new_app_env = app_manifest.environment
            new_app_env["AGENT_HOST"] = app_host

            # Step 1.2: Extract DNS extra hosts from the edge admin container

            edge_admin_container = docker_client.containers.get(edge_app_name)
            if edge_admin_container is None:
                raise Exception(f"Edge app container {edge_app_name} not found")

            extra_hosts_list = edge_admin_container.attrs["HostConfig"].get(
                "ExtraHosts", []
            )
            extra_hosts_dict = dict(
                entry.split(":", 1) for entry in extra_hosts_list if ":" in entry
            )

            # Step 1.3: Run the new container

            docker_client.containers.run(
                image=app_manifest.image,
                name=f"{app_manifest.name}",
                detach=True,
                environment=new_app_env,
                ports=app_manifest.ports,
                command=app_manifest.command,
                extra_hosts=extra_hosts_dict,
            )

            # Step 2: Read the new verkey
            web_port = 5002
            if app_manifest.name == "ma-ssi-car-twin":
                web_port = 5002
            elif app_manifest.name == "ma-ssi-drone-twin":
                web_port = 5005
            else:
                raise Exception("Unknown app name")

            base_url = f"http://{app_host}:{web_port}"

            new_verkey = await get_new_app_verkey(base_url)

            if new_verkey is None:
                raise Exception("Failed to get new verkey from the migrated app")

            # Step 3: Return the new verkey and container name to the source edge

            print(f"New verkey: {new_verkey}.")

            new_app_info = AppMigrationNewAppInfo(
                app_name=app_manifest.name, new_verkey=new_verkey
            )

            app_deployment_end = time.perf_counter()
            metrics_logger.info(f"[App Migration] App deployment completed in {app_deployment_end - app_deployment_start} seconds")

        elif (
            req.connection_type == ApplicationConnectionType.TWIN_CAR_TO_EDGE
            or req.connection_type == ApplicationConnectionType.TWIN_DRONE_TO_EDGE
        ):

            # Role: Source Edge

            handover_start = time.perf_counter()

            # Step 1: Send request to the other edge

            new_app_info = await request_application_migration(app_manifest)

            # Step 2: Return the new verkey and container name to the old app

            # Schedule app shutdown when the verkey is published
            app_did = req_wrapper.did_exchange.conn.their_public_did
            app_did = app_did if app_did != None else ""

            background_tasks.add_task(
                schedule_app_shutdown_on_new_verkey_registration,
                app_name=app_manifest.name,
                app_did=app_did,
                new_verkey=new_app_info.new_verkey,
            )

            handover_end = time.perf_counter()
            metrics_logger.info(f"[App Migration] App handover request completed in {handover_end - handover_start} seconds")

        # Send the new app info to the requester
        if new_app_info == None:
            raise Exception("Failed getting new app info!")

        await basicmessage_send_message(
            agent,
            connection_id=conn.connection_id,
            content=new_app_info.model_dump_json(),
        )

        return

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e

        print(e)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clear the connection
        await didexchange_clear_connection(agent, conn.connection_id)
