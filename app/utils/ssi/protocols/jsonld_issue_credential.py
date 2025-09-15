from typing import Any, Mapping
from acapy_controller import Controller
from acapy_controller.protocols import (
    V20CredExRecord,
    V20CredExRecordDetail,
)


async def jsonld_issue_credential_issuer_send_offer(
    issuer: Controller,
    issuer_connection_id: str,
    credential: Mapping[str, Any],
    options: Mapping[str, Any],
) -> V20CredExRecord:
    issuer_cred_ex = await issuer.post(
        "/issue-credential-2.0/send-offer",
        json={
            "auto_issue": False,
            "auto_remove": False,
            "comment": "Credential from minimal example",
            "trace": False,
            "connection_id": issuer_connection_id,
            "filter": {
                "ld_proof": {
                    "credential": credential,
                    "options": options,
                }
            },
        },
        response=V20CredExRecord,
    )

    return issuer_cred_ex


async def jsonld_issue_credential_issuer_handle_request(
    issuer: Controller, cred_ex_id: str
) -> V20CredExRecord:
    await issuer.event_with_values(
        topic="issue_credential_v2_0",
        cred_ex_id=cred_ex_id,
        state="request-received",
    )

    issuer_cred_ex = await issuer.post(
        f"/issue-credential-2.0/records/{cred_ex_id}/issue",
        json={},
        response=V20CredExRecordDetail,
    )

    issuer_cred_ex = await issuer.event_with_values(
        topic="issue_credential_v2_0",
        event_type=V20CredExRecord,
        cred_ex_id=cred_ex_id,
        state="done",
    )

    return issuer_cred_ex


async def jsonld_issue_credential_holder_wait_for_offer(
    holder: Controller, holder_connection_id: str
) -> V20CredExRecord:
    holder_cred_ex = await holder.event_with_values(
        topic="issue_credential_v2_0",
        event_type=V20CredExRecord,
        connection_id=holder_connection_id,
        state="offer-received",
    )

    return holder_cred_ex


async def jsonld_issue_credential_holder_send_request(
    holder: Controller, holder_cred_ex_id: str
) -> V20CredExRecord:
    holder_cred_ex = await holder.post(
        f"/issue-credential-2.0/records/{holder_cred_ex_id}/send-request",
        response=V20CredExRecord,
    )

    return holder_cred_ex


async def jsonld_issue_credential_holder_receive_credential(
    holder: Controller, holder_cred_ex_id: str
) -> V20CredExRecord:
    await holder.event_with_values(
        topic="issue_credential_v2_0",
        cred_ex_id=holder_cred_ex_id,
        state="credential-received",
    )

    holder_cred_ex = await holder.post(
        f"/issue-credential-2.0/records/{holder_cred_ex_id}/store",
        json={},
        response=V20CredExRecordDetail,
    )

    holder_cred_ex = await holder.event_with_values(
        topic="issue_credential_v2_0",
        event_type=V20CredExRecord,
        cred_ex_id=holder_cred_ex_id,
        state="done",
    )

    return holder_cred_ex
