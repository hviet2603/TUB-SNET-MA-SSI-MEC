from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentConfig:
    name: Optional[str]
    host: Optional[str] 
    agent_port: Optional[int] 
    agent_admin_port: Optional[int]
    did: Optional[str]
    seed: Optional[str]