import asyncio
import json
import logging
import re
<<<<<<< HEAD
from threading import Lock
=======
>>>>>>> faeb402eaab518858020bc1b6d4aef221a395b6b

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.config import get_settings

logger = logging.getLogger(__name__)

MAX_TOKENS_ESTIMATE = 6000
MAX_RETRIES = 2
BASE_DELAY = 0.5
LLM_CONCURRENCY = 25

_llm_semaphore = asyncio.Semaphore(LLM_CONCURRENCY)


def _estimate_tokens(text: str) -> int:
    return len(text) // 3


def _truncate_input(content: str, max_tokens: int = MAX_TOKENS_ESTIMATE) -> str:
    if _estimate_tokens(content) <= max_tokens:
        return content
    half = max_tokens * 3 // 2
    return content[:half] + "\n[...input truncated...]\n" + content[-half:]


def _extract_json(content: str) -> dict:
    content = content.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    json_objects = re.findall(r'\{(?:[^{}]|\{[^{}]*\})*\}', content)
    for candidate in sorted(json_objects, key=len, reverse=True):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    raise ValueError(f"No valid JSON found in response: {content[:300]}")


class LLMProvider:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        settings = get_settings()
        self._settings = settings
        self._openai = None
        self._build_client()

    def _build_client(self):
        model_name = "deepseek-v4-pro"
        kwargs = {
            "model": model_name,
            "api_key": self._settings.openai_api_key,
            "temperature": 0.1,
        }
        if self._settings.openai_api_base:
            kwargs["base_url"] = self._settings.openai_api_base
        else:
            kwargs["base_url"] = "https://api.deepseek.com/v1"
        self._openai = ChatOpenAI(**kwargs)
        logger.info("LLM backend: DeepSeek with model %s", model_name)

    async def complete(
        self,
        messages: list[dict],
        response_model: type[BaseModel] | None = None,
    ) -> str | BaseModel:
<<<<<<< HEAD
        if not self._openai:
            raise RuntimeError("No LLM API key configured. Set OPENAI_API_KEY.")

        for msg in messages:
            if isinstance(msg.get("content"), str):
                msg["content"] = _truncate_input(msg["content"])

        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                async with _llm_semaphore:
                    result = await self._openai.ainvoke(messages)
                content = result.content
                if response_model:
                    data = _extract_json(content)
                    return response_model(**data)
                return content
            except ValueError as e:
                logger.warning(
                    "LLM JSON parse failed (attempt %d/%d): %s",
                    attempt + 1, MAX_RETRIES, e,
                )
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(BASE_DELAY * (2 ** attempt))
            except Exception as e:
                logger.warning(
                    "LLM call failed (attempt %d/%d): %s",
                    attempt + 1, MAX_RETRIES, e,
                )
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(BASE_DELAY * (2 ** attempt))

        raise RuntimeError(f"LLM call failed after {MAX_RETRIES} attempts: {last_error}")

    async def complete_batch(
        self,
        tasks: list[dict],
        response_model: type[BaseModel] | None = None,
    ) -> list[str | BaseModel]:
        """Batch complete multiple conversations concurrently."""
        async def _process(task):
            messages = task["messages"]
            for msg in messages:
                if isinstance(msg.get("content"), str):
                    msg["content"] = _truncate_input(msg["content"])

            for attempt in range(MAX_RETRIES):
                try:
                    async with _llm_semaphore:
                        result = await self._openai.ainvoke(messages)
                    content = result.content
                    if response_model:
                        data = _extract_json(content)
                        return response_model(**data)
                    return content
                except Exception:
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(BASE_DELAY * (2 ** attempt))
            return None

        results = await asyncio.gather(*[_process(task) for task in tasks])
        return results
=======
        """Complete a conversation. Returns parsed response_model or raw string."""
        if not self._openai:
            raise RuntimeError(
                "No LLM API key configured. Set OPENAI_API_KEY."
            )

        # Use DeepSeek V4
        result = await self._openai.ainvoke(messages)
        content = result.content
        if response_model:
            data = _extract_json(content)
            return response_model(**data)
        return content
>>>>>>> faeb402eaab518858020bc1b6d4aef221a395b6b
