from ..models.web.vc import VC_TYPE, VP_DEF_DETAILS_TEMPLATE
from typing import Dict, Any
from uuid import uuid4

def create_vp_definition(vc_type: VC_TYPE, schema_uri: str) -> Dict[str, Any]:
    vp_details = VP_DEF_DETAILS_TEMPLATE.get(vc_type, {})
    return {
        "input_descriptors": [
            {
                "id": f"{vc_type.value}_vp",
                "name": f"{vc_type.value} VP",
                "schema": [
                    {
                        "uri": "https://www.w3.org/2018/credentials#VerifiableCredential"  
                    },
                    {
                        "uri": schema_uri
                    }
                ],
                **vp_details,
            }
        ],
        "id": str(uuid4()),
        "format": {"ldp_vp": {"proof_type": ["Ed25519Signature2018"]}},
    }