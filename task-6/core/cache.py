
import redis.asyncio as redis
import json
from typing import Optional

class RedisCache:
    def __init__(self, url: str):
        self.client = redis.from_url(url, decode_responses=True)

    async def get(self, key: str) -> Optional[dict]:
        data = await self.client.get(f"cache:{key}")
        return json.loads(data) if data else None

    async def set(self, key: str, value: dict, ttl: int):
        await self.client.setex(f"cache:{key}", ttl, json.dumps(value))

    async def get_ttl(self, key: str) -> int:
        return await self.client.ttl(f"cache:{key}")

    async def close(self):
        await self.client.close()
