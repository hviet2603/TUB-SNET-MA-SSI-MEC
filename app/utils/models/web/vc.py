from typing import Dict, Any
from pydantic import BaseModel
from enum import Enum


class VCIssuanceInitRequestModel(BaseModel):
    type: str = "vc_init_vc_issuance"
    invite: Dict[str, Any]


class VPExchangeInitRequestModel(BaseModel):
    type: str = "vc_init_vp_exchange"
    invite: Dict[str, Any]


class VC_TYPE(str, Enum):
    EDGE = "Edge"
    CAR_TWIN = "CarTwin"
    DRONE_TWIN = "DroneTwin"
    CAR = "Car"
    DRONE = "Drone"
    CAR_CAPABILITY_DELEGATION = "CarCapabilityDelegation"


VP_DEF_DETAILS_TEMPLATE = {
    VC_TYPE.EDGE: {
        "constraints": {
            # "is_holder": [
            #    {
            #        "directive": "required",
            #        "field_id": ["1f44d55f-f161-4938-a659-f8026467f126"],
            #    }
            # ],
            "fields": [
                {
                    # "id": "1f44d55f-f161-4938-a659-f8026467f126",
                    "path": ["$.credentialSubject.name"],
                    "purpose": "To show the name of the edge node",
                }
            ]
        },
    },
    VC_TYPE.CAR_TWIN: {
        "constraints": {
            "fields": [
                {
                    "path": ["$.credentialSubject.name"],
                    "purpose": "To show the name of the car twin",
                },
                {
                    "path": ["$.credentialSubject.car_twin_id"],
                    "purpose": "To show the ID of the car twin",
                },
                {
                    "path": ["$.credentialSubject.car_id"],
                    "purpose": "To show the ID of the car associated with the twin",
                },
            ]
        },
    },
    VC_TYPE.DRONE_TWIN: {
        "constraints": {
            "fields": [
                {
                    "path": ["$.credentialSubject.name"],
                    "purpose": "To show the name of the drone twin",
                },
                {
                    "path": ["$.credentialSubject.drone_twin_id"],
                    "purpose": "To show the ID of the drone twin",
                },
                {
                    "path": ["$.credentialSubject.drone_id"],
                    "purpose": "To show the ID of the drone associated with the twin",
                },
            ]
        },
    },
    VC_TYPE.CAR: {
        "constraints": {
            "fields": [
                {
                    "path": ["$.credentialSubject.name"],
                    "purpose": "To show the name of the car",
                },
                {
                    "path": ["$.credentialSubject.car_twin_id"],
                    "purpose": "To show the ID of the car twin",
                },
                {
                    "path": ["$.credentialSubject.car_id"],
                    "purpose": "To show the ID of the car associated with the twin",
                },
            ]
        },
    },
    VC_TYPE.DRONE: {
        "constraints": {
            "fields": [
                {
                    "path": ["$.credentialSubject.name"],
                    "purpose": "To show the name of the drone",
                },
                {
                    "path": ["$.credentialSubject.drone_twin_id"],
                    "purpose": "To show the ID of the drone twin",
                },
                {
                    "path": ["$.credentialSubject.drone_id"],
                    "purpose": "To show the ID of the drone associated with the twin",
                },
            ]
        },
    },
    VC_TYPE.CAR_CAPABILITY_DELEGATION: {
        "constraints": {
            "fields": [
                {
                    "path": ["$.credentialSubject.car_twin_id"],
                    "purpose": "To show the ID of the car twin",
                },
                {
                    "path": ["$.credentialSubject.car_id"],
                    "purpose": "To show the ID of the car associated with the twin",
                },
                {
                    "path": ["$.credentialSubject.capability_delegation"],
                    "purpose": "To show the delegated capabilities for the car's twin",
                },
            ]
        }
    }
}
