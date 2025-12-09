from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.utils.agent import create_agent
from .env_config import get_agent_config
from .utils.vc import request_vc
from .routes.apps.apps import router as apps_router
from .utils.application import request_application_migration
from app.utils.utils import set_timeout

@asynccontextmanager
async def lifespan(app: FastAPI):
    agent_config = get_agent_config()
    agent_process = await create_agent(agent_config)
    
    # Request for VC
    await request_vc()

    # Request for application migration
    #if "beta" in agent_config.name:
    #    set_timeout(request_application_migration, 5)

    yield
    
    agent_process.kill()

app = FastAPI(lifespan=lifespan)

app.include_router(apps_router)


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
    
