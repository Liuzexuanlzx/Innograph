from pathlib import Path

from pydantic_settings import BaseSettings
from functools import lru_cache

# Resolve .env from project root (two levels up from this file: app/config.py -> backend -> project root)
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "innograph_dev"

    redis_url: str = "redis://localhost:6379/0"

    openai_api_key: str = ""
    openai_api_base: str = ""
    anthropic_api_key: str = ""

    openalex_email: str = ""
    s2_api_key: str = ""

    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"

    model_config = {"env_file": str(_ENV_FILE), "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
