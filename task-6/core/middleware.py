
import time
from redis.asyncio import Redis

class RedisRateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def is_allowed(self, client_id: str, limit: int = 50, window: int = 60) -> tuple[bool, str]:
        key = f"ratelimit:{client_id}"
        
        # Atomically increment and set expiry if new
        async with self.redis.pipeline(transaction=True) as pipe:
            await pipe.incr(key)
            await pipe.expire(key, window, nx=True)
            results = await pipe.execute()
        
        count = results[0]
        allowed = count <= limit
        status = f"{count}/{limit} req/min"
        return allowed, status
