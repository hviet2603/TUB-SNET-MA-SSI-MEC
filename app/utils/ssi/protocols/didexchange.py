from acapy_controller import Controller
from acapy_controller.protocols import (
    params,
    InvitationRecord,
    InvitationMessage,
    OobRecord,
    ConnRecord,
)
import asyncio


async def didexchange_inviter_create_invitation(
    inviter: Controller,
    public_did: str,
    multi_use: bool = False,
) -> InvitationMessage:
    invite_record = await inviter.post(
        "/out-of-band/create-invitation",
        json={
            "handshake_protocols": ["https://didcomm.org/didexchange/1.1"],
            "use_did": public_did
        },
        params=params(
            auto_accept=False,
            multi_use=multi_use,
        ),
        response=InvitationRecord,
    )

    return invite_record.invitation


async def didexchange_invitee_accept_invitation(
    invitee: Controller, invite: InvitationMessage
) -> ConnRecord:
    oob_record = await invitee.post(
        "/out-of-band/receive-invitation",
        json=invite,
        params=params(
            use_existing_connection=False,
        ),
        response=OobRecord,
    )

    conn = await invitee.post(
        f"/didexchange/{oob_record.connection_id}/accept-invitation",
        response=ConnRecord,
    )

    return conn


async def didexchange_inviter_handle_request(
    inviter: Controller, invite: InvitationMessage
) -> ConnRecord:

    oob_record = await inviter.event_with_values(
        topic="out_of_band",
        invi_msg_id=invite.id,
        state="done",
        event_type=OobRecord,
    )

    conn = await inviter.event_with_values(
        topic="connections",
        event_type=ConnRecord,
        rfc23_state="request-received",
        invitation_key=oob_record.our_recipient_key,
    )

    await asyncio.sleep(1)

    conn = await inviter.post(
        f"/didexchange/{conn.connection_id}/accept-request",
        response=ConnRecord,
    )

    conn = await inviter.event_with_values(
        topic="connections",
        connection_id=conn.connection_id,
        rfc23_state="completed",
        event_type=ConnRecord,
    )

    return conn


async def didexchange_invitee_handle_response(
    invitee: Controller, connection_id
) -> ConnRecord:

    await invitee.event_with_values(
        topic="connections",
        connection_id=connection_id,
        rfc23_state="response-received",
    )
    
    conn = await invitee.event_with_values(
        topic="connections",
        connection_id=connection_id,
        rfc23_state="completed",
        event_type=ConnRecord,
    )
    
    return conn

async def didexchange_clear_connection(agent: Controller, connection_id: str):
    await agent.delete(f"/connections/{connection_id}")
