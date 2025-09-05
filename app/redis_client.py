import logging
import os
from dotenv import load_dotenv
import redis.asyncio as redis

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
if(REDIS_URL is None):
    raise ValueError("REDIS_URL environment variable not set")

redis_client: redis.Redis | None = None

async def init_redis_pool():
    global redis_client
    if redis_client is not None:
        return redis_client

    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    await redis_client.ping()
    logging.info(f"Redis client initialized and connected to {REDIS_URL}")
    return redis_client


async def close_redis_pool():
    """
    Close the redis connection cleanly.
    """
    global redis_client
    if redis_client:
        try:
            await redis_client.close()
        except Exception:
            pass
        redis_client = None
