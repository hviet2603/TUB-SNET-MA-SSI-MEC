from pydantic import BaseModel
from acapy_controller.protocols import ConnRecord

class DIDExchangeContextModel(BaseModel):
    conn: ConnRecord

    class Config:
        arbitrary_types_allowed = True