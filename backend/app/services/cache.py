import json
from typing import Any

import redis.asyncio as aioredis

from app.config import get_settings

TTL_API = 86400       # 24 hours for API responses
TTL_LLM = 604800      # 7 days for LLM extractions


class CacheService:
    def __init__(self, client: aioredis.Redis | None = None):
        if client:
            self._redis = client
        else:
            settings = get_settings()
            self._redis = aioredis.from_url(settings.redis_url, decode_responses=True)

    async def get(self, key: str) -> Any | None:
        val = await self._redis.get(key)
        if val is None:
            return None
        return json.loads(val)

    async def set(self, key: str, value: Any, ttl: int = TTL_API) -> None:
        await self._redis.set(key, json.dumps(value, default=str), ex=ttl)

    async def get_paper_card(self, paper_id: str) -> dict | None:
        return await self.get(f"paper_card:{paper_id}")

    async def set_paper_card(self, paper_id: str, card: dict) -> None:
        await self.set(f"paper_card:{paper_id}", card, ttl=TTL_LLM)

    async def get_edge(self, source_id: str, target_id: str) -> dict | None:
        return await self.get(f"edge:{source_id}:{target_id}")

    async def set_edge(self, source_id: str, target_id: str, edge: dict) -> None:
        await self.set(f"edge:{source_id}:{target_id}", edge, ttl=TTL_LLM)

    async def get_api_response(self, key: str) -> dict | None:
        return await self.get(f"api:{key}")

    async def set_api_response(self, key: str, data: dict) -> None:
        await self.set(f"api:{key}", data, ttl=TTL_API)
