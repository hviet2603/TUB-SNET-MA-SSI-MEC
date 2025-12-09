from acapy_controller import Controller

async def basicmessage_send_message(
    sender: Controller,
    connection_id: str,
    content: str,
) -> None:

    res = await sender.post(
        f"/connections/{connection_id}/send-message",
        json={
            "content": content,
        },
    )

async def basicmessage_receive_message(
    receiver: Controller,
    connection_id: str,
    timeout: int = 5,
) -> str:

    payload = await receiver.event_with_values(
        topic="basicmessages",
        connection_id=connection_id,
        state="received",
        timeout=timeout
    )

    return payload.get("content")