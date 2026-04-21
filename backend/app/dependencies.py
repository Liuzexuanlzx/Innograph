from typing import Annotated

from fastapi import Depends
from neo4j import AsyncGraphDatabase, AsyncDriver
import redis.asyncio as aioredis

from app.config import Settings, get_settings


async def get_neo4j_driver(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncDriver:
    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )
    return driver


async def get_redis(
    settings: Annotated[Settings, Depends(get_settings)],
) -> aioredis.Redis:
    return aioredis.from_url(settings.redis_url, decode_responses=True)
