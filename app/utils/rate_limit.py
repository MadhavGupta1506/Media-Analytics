from fastapi import HTTPException
from app.redis_client import redis_client
from collections import defaultdict

RATE_LIMIT = 20
WINDOW = 60
import logging

# In-memory rate limit for when Redis is not available (e.g., tests)
in_memory_counts = defaultdict(int)

async def rate_limit_ip_media(ip: str, media_id: str):
    global redis_client
    if redis_client is None:
        logging.warning("Redis client not initialized in rate limiter, using in-memory")
        key = f"{ip}:{media_id}"
        in_memory_counts[key] += 1
        count = in_memory_counts[key]
        logging.info(f"In-memory rate limit key={key} count={count}")
        if count > RATE_LIMIT:
            logging.warning(f"Rate limit exceeded for key {key}")
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {RATE_LIMIT} requests per {WINDOW} seconds."
            )
        return

    key = f"rate:{ip}:{media_id}"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, WINDOW)

    logging.info(f"Rate limit key={key} count={count}")

    if count > RATE_LIMIT:
        logging.warning(f"Rate limit exceeded for key {key}")
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT} requests per {WINDOW} seconds."
        )
