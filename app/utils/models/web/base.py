from pydantic import BaseModel
from .didexchange import DIDExchangeContextModel
from .vc import VCIssuanceInitRequestModel, VPExchangeInitRequestModel
from .application import (
    AppMigrationInitRequestModel,
)
from .capability_delegation import CapabilityDelegationRequestModel
from .car_position import CarPositionRequestModel
from acapy_controller import Controller
from typing import Dict, Any, List
from ..ssi.agent import AgentConfig

SSIRequestModel = (
    VCIssuanceInitRequestModel
    | VPExchangeInitRequestModel
    | AppMigrationInitRequestModel
    | CapabilityDelegationRequestModel
    | CarPositionRequestModel
)

class SSIRequestWithContext(BaseModel):
    req: SSIRequestModel
    agent: Controller
    agent_config: AgentConfig
    did_exchange: DIDExchangeContextModel
    credentials: List[Dict[str, Any]] = []

    class Config:
        arbitrary_types_allowed = True
