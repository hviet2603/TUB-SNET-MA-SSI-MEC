from pydantic import BaseModel
from typing import Dict, Any

class CapabilityDelegationRequestModel(BaseModel):
    type: str = "capability_delegation"
    invite: Dict[str, Any]