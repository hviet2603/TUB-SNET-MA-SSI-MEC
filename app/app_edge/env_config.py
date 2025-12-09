import os
from dataclasses import asdict

from app.utils.models.ssi.agent import AgentConfig
from ..global_config import DID_PREFIX

AUTHORITY_WEB_URL = os.getenv("AUTHORITY_WEB_URL", "http://localhost:3002")
EDGE_ALPHA_WEB_URL = os.getenv("EDGE_ALPHA_WEB_URL", "http://localhost:4002")
EDGE_BETA_WEB_URL = os.getenv("EDGE_BETA_WEB_URL", "http://localhost:4005")   

def get_agent_config() -> AgentConfig:
    return AgentConfig(
        host =  os.getenv("AGENT_HOST", "localhost"),
        agent_port = int(os.getenv("AGENT_PORT", 4000)),
        agent_admin_port = int(os.getenv("AGENT_ADMIN_PORT", 4001)),
        name = os.getenv("AGENT_LABEL", "edge_alpha"), 
        seed = os.getenv("AGENT_SEED", "edgealpha00000000000000000000000"),
        did = f"{DID_PREFIX}{os.getenv("AGENT_INDY_NYM", "LFrSJFNqGcfUZk11LCwbfJ")}",   
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