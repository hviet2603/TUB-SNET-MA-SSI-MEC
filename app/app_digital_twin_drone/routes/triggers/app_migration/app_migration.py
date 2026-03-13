from fastapi import APIRouter, HTTPException
import time

from app.utils.vdr.vdr import change_verkey
from app.utils.logger import get_logger
from ....env_config import get_agent_config, EDGE_NAME, EDGE_ALPHA_WEB_URL, EDGE_BETA_WEB_URL, AUTHORITY_WEB_URL, CAR_WEB_URL
from ....utils.triggers import trigger_application_migration
from .....utils.models.web.application import AppMigrationNewAppInfo, ApplicationManifestModel

router = APIRouter(prefix="/app_migration", tags=["app_migration"])

metric_logger = get_logger()

""" Send initiate app migration request to source edge from digital twin car app """

@router.post("/")
async def app_migration():
    try:

        web_port = 5005
        app_name = "ma-ssi-drone-twin"

        src_edge_url = EDGE_ALPHA_WEB_URL
        
        if EDGE_NAME == "edge_beta":
            src_edge_url = EDGE_BETA_WEB_URL

        agent_config = get_agent_config()
        
        new_app_info : AppMigrationNewAppInfo = await trigger_application_migration(
            base_url=src_edge_url,
            app_manifest=ApplicationManifestModel(
                name=app_name,
                image="vdocker2603/ma-ssi-apps:latest",
                environment={
                    "AUTHORITY_WEB_URL": AUTHORITY_WEB_URL,
                    "EDGE_ALPHA_WEB_URL": EDGE_ALPHA_WEB_URL,
                    "EDGE_BETA_WEB_URL": EDGE_BETA_WEB_URL,
                    "CAR_WEB_URL": CAR_WEB_URL,
                    "EDGE_NAME": "edge_beta" if EDGE_NAME == "edge_alpha" else "edge_alpha",
                    "AGENT_PORT": str(agent_config.agent_port),
                    "AGENT_ADMIN_PORT": str(agent_config.agent_admin_port),
                    "AGENT_LABEL": agent_config.name,
                    "AGENT_SEED": agent_config.seed,
                    "AGENT_INDY_NYM": agent_config.did.split(":")[2],
                    "MIGRATION": "true"
                },
                ports={
                    f"{agent_config.agent_port}/tcp": str(agent_config.agent_port),
                    f"{agent_config.agent_admin_port}/tcp": str(agent_config.agent_admin_port),
                    f"{web_port}/tcp": str(web_port)
                },
                command=f"uvicorn app.app_digital_twin_drone.main:app --host 0.0.0.0 --port {str(web_port)}",              
            )
        )

        # Register the new verkey
        print(f"The application is started on other host, new verkey is: {new_app_info.new_verkey}")

        change_verkey_start = time.perf_counter()
        await change_verkey(
            seed=agent_config.seed,
            new_verkey=new_app_info.new_verkey,
            did=agent_config.did.split(":")[-1]
        )
        change_verkey_end = time.perf_counter()
        metric_logger.info(f"[App Migration] Verkey change completed in {change_verkey_end - change_verkey_start} seconds")

        return

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e

        print(e)
        raise HTTPException(status_code=500, detail=str(e))
