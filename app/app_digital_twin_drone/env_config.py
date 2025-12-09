import os
from dataclasses import asdict

from app.utils.models.ssi.agent import AgentConfig
from ..global_config import DID_PREFIX

AUTHORITY_WEB_URL = os.getenv("AUTHORITY_WEB_URL", "http://localhost:3002")
EDGE_ALPHA_WEB_URL = os.getenv("EDGE_ALPHA_WEB_URL", "http://localhost:4002")
EDGE_BETA_WEB_URL = os.getenv("EDGE_BETA_WEB_URL", "http://localhost:4005")
EDGE_NAME = os.getenv("EDGE_NAME", "edge_alpha")

def get_agent_config() -> AgentConfig:
    
    tmp_seed = os.getenv("AGENT_SEED", "dronetwin00000000000000000000000")
    
    if EDGE_NAME == "edge_alpha":
        tmp_seed = tmp_seed[:-1] + "0"
    else:
        tmp_seed = tmp_seed[:-1] + "1"

    return AgentConfig(
        host =  os.getenv("AGENT_HOST", "localhost"),
        agent_port = int(os.getenv("AGENT_PORT", 5003)),
        agent_admin_port = int(os.getenv("AGENT_ADMIN_PORT", 5002)),
        name = os.getenv("AGENT_LABEL", "drone_twin"), 
        seed = tmp_seed,
        did = f"{DID_PREFIX}{os.getenv("AGENT_INDY_NYM", "4ZRTENo4kDF2mHb2xXct25")}",   
    )

def update_agent_config(config: AgentConfig):
    for key, value in asdict(config).items():
        if value:
            env_var_dict = {
                "host": "AGENT_HOST",
                "agent_port": "AGENT_PORT",
                "agent_admin_port": "AGENT_ADMIN_PORT",
                "name": "AGENT_LABEL", 
                "seed": "AGENT_SEED",
                "did": "AGENT_INDY_NYM",
            }
            
            if key == "did":
                pass
            else:
                env_var_name = env_var_dict[key]
                os.environ[env_var_name] = str(value)