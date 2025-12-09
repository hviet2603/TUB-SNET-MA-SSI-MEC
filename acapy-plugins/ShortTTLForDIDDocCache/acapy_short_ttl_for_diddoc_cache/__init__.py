"""Short TTL InMem-Cache Injection"""

from .cache import ShortTTLForDIDDocCache
from acapy_agent.config.injection_context import InjectionContext
from acapy_agent.cache.base import BaseCache

async def setup(context: InjectionContext):
    
    cache_inst = ShortTTLForDIDDocCache()
    context.injector.bind_instance(BaseCache, cache_inst)