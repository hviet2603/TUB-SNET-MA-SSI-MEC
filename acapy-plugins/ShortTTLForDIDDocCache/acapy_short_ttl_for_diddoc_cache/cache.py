from acapy_agent.cache.in_memory import InMemoryCache
import time
from typing import Any, Optional, Sequence, Text, Union
import re

class ShortTTLForDIDDocCache(InMemoryCache):

    MAX_TTL = 3

    def __init__(self):
        super().__init__()

    async def set(
        self, keys: Union[Text, Sequence[Text]], value: Any, ttl: Optional[int] = None
    ):
        """Add an item to the cache with an optional ttl.

        Overwrites existing cache entries.

        Args:
            keys: the key or keys for which to set an item
            value: the value to store in the cache
            ttl: number of seconds that the record should persist

        """
        self._remove_expired_cache_items()
        
        # Check if it a entry for a DIDDoc and if the TTL exceeds

        diddoc_key_pattern = re.compile(r"^resolver::.*::.*")

        for key in [keys] if isinstance(keys, Text) else keys:
            if diddoc_key_pattern.match(key) != None:
                if ttl:
                    if ttl > ShortTTLForDIDDocCache.MAX_TTL:
                        ttl = ShortTTLForDIDDocCache.MAX_TTL
                        break

        expires_ts = time.perf_counter() + ttl if ttl else None
        for key in [keys] if isinstance(keys, Text) else keys:
            self._cache[key] = {"expires": expires_ts, "value": value}
