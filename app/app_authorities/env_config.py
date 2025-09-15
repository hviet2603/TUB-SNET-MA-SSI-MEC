import os
from dataclasses import asdict

from app.utils.models.ssi.agent import AgentConfig

WEB_PORT = int(os.getenv("WEB_PORT", 3002))

def get_agent_config() -> AgentConfig:
    return AgentConfig(
        host =  os.getenv("AGENT_HOST", "localhost"),
        agent_port = int(os.getenv("AGENT_PORT", 3000)),
        agent_admin_port = int(os.getenv("AGENT_ADMIN_PORT", 3001)),
        name = os.getenv("AGENT_LABEL", "authorities"), 
        seed = os.getenv("AGENT_SEED", "authoritiesrepresentation0000000"),
        did = f"did:indy:{os.getenv("AGENT_INDY_DID", "5BcajonJVd8L9dmvgDr1pB")}",   
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
                "did": "AGENT_INDY_DID",
            }
            
            if key == "did":
                pass
            else:
                env_var_name = env_var_dict[key]
                os.environ[env_var_name] = str(value)