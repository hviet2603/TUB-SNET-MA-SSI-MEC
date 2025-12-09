from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.app_digital_twin_car.utils.vc import request_vc
from app.app_digital_twin_car.utils.application import publish_agent_on_new_verkey_registration
from app.utils.agent import create_agent
from .env_config import get_agent_config
from .routes.triggers.triggers import router as triggers_router
from .routes.apps.apps import router as apps_router
import os
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    agent_config = get_agent_config()
    
    migration = True if os.getenv("MIGRATION", "false").lower() == "true" else False

    create_public_agent_did = not migration

    agent_process = await create_agent(agent_config, create_public_agent_did=create_public_agent_did)

    if migration == False:
        # Request for VC
        await request_vc()
    else:
        asyncio.create_task(
            publish_agent_on_new_verkey_registration(agent_config.did)
        )

    yield
    
    agent_process.kill()

app = FastAPI(lifespan=lifespan)

app.include_router(triggers_router)
app.include_router(apps_router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
    
