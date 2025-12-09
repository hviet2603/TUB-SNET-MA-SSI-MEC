from typing import Any, Mapping
from acapy_controller import Controller
from acapy_controller.protocols import (
    V20PresExRecord,
)
from acapy_controller.models import V20PresExRecord as V20PresExRecordModel

from uuid import uuid4


async def jsonld_present_proof_prover_send_proof(
    prover: Controller,
    prover_connection_id: str,
) -> V20PresExRecord:
    pres_ex = await prover.event_with_values(
        topic="present_proof_v2_0",
        event_type=V20PresExRecord,
        connection_id=prover_connection_id,
        state="request-received",
    )

    attachment = pres_ex.pres_request["request_presentations~attach"][0]
    definition = attachment["data"]["json"]["presentation_definition"]

    pres_ex = await prover.post(
        f"/present-proof-2.0/records/{pres_ex.pres_ex_id}/send-presentation",
        json={"dif": {"presentation_definition": definition}},
        response=V20PresExRecord,
    )

    pres_ex = await prover.event_with_values(
        topic="present_proof_v2_0",
        event_type=V20PresExRecord,
        pres_ex_id=pres_ex.pres_ex_id,
        state="done",
    )

    return pres_ex


async def jsonld_present_proof_verifier_send_request(
    verifier: Controller,
    verifier_connection_id: str,
    vp_definition: Mapping[str, Any],
    comment: str = "U really that guy?",
) -> V20PresExRecord:
    pres_ex = await verifier.post(
        "/present-proof-2.0/send-request",
        json={
            "auto_verify": False,
            "comment": comment,
            "connection_id": verifier_connection_id,
            "presentation_request": {
                "dif": {
                    "options": {
                        "challenge": str(uuid4()),
                        "domain": "masterabeit-ssi",
                    },
                    "presentation_definition": vp_definition,
                }
            },
            "trace": False,
        },
        response=V20PresExRecord,
    )

    return pres_ex


async def jsonld_present_proof_verifier_receive_presentation(
    verifier: Controller,
    pres_ex_id: str,
) -> V20PresExRecord:
    pres_ex = await verifier.event_with_values(
        topic="present_proof_v2_0",
        event_type=V20PresExRecord,
        pres_ex_id=pres_ex_id,
        state="presentation-received",
    )

    # credentials = pres_ex.by_format._extra["pres"]["dif"]["verifiableCredential"]
    # print(credentials)

    return pres_ex


async def jsonld_present_proof_verifier_verify_presentation(
    verifier: Controller,
    pres_ex_id: str,
) -> V20PresExRecord:
    pres_ex = await verifier.post(
        f"/present-proof-2.0/records/{pres_ex_id}/verify-presentation",
        json={},
        response=V20PresExRecordModel,
    )

    if pres_ex.verified != "true":
        raise Exception("Presentation verification failed")

    pres_ex = await verifier.event_with_values(
        topic="present_proof_v2_0",
        event_type=V20PresExRecord,
        pres_ex_id=pres_ex.pres_ex_id,
        state="done",
    )

    return pres_ex
