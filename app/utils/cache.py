from typing import Any
from datetime import timedelta

from ..redis_client import redis_client

CACHE_TTL_SECONDS = 60  # short TTL for analytics maybe 60s, tweak as needed

async def get_cached(key: str):
    if not redis_client:
        return None
    val = await redis_client.get(key)
    return None if val is None else val

async def set_cached(key: str, value: str, ttl: int = CACHE_TTL_SECONDS):
    if not redis_client:
        return
    await redis_client.set(key, value, ex=ttl)
