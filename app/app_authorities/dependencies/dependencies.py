from ..env_config import get_agent_config
from app.utils.models.web.base import SSIRequestWithContext, SSIRequestModel
from app.utils.web.req_context_wrapper import wrap_request_with_DIDExchange_context

async def get_request_with_DIDExchange_context(
    req: SSIRequestModel,
) -> SSIRequestWithContext:
    agent_config = get_agent_config()                     
    
    return await wrap_request_with_DIDExchange_context(agent_config, req)
