from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.utils.models.ssi.agent import AgentConfig
from app.utils.agent import create_agent, create_agent_admin_url
from .env_config import get_agent_config

from .routes.vc import router as vc_router 

@asynccontextmanager
async def lifespan(app: FastAPI):
    agent_config = get_agent_config()
    agent_process = await create_agent(agent_config)
    
    yield
    
    agent_process.kill()

app = FastAPI(lifespan=lifespan)

app.include_router(vc_router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
    
