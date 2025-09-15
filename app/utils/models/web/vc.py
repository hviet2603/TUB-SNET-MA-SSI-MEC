from pydantic import BaseModel
from typing import Dict, Any

class VCIssuanceInitRequestModel(BaseModel):
    invite: Dict[str, Any]