from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.app_car.utils.vc import request_vc
from app.utils.agent import create_agent
from .env_config import get_agent_config

@asynccontextmanager
async def lifespan(app: FastAPI):
    agent_config = get_agent_config()
    

    agent_process = await create_agent(agent_config)

    # Request for VC
    await request_vc()

    yield
    
    agent_process.kill()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
    
