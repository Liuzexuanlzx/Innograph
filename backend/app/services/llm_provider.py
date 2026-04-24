import json
import logging
import re

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.config import get_settings

logger = logging.getLogger(__name__)


def _extract_json(content: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    content = content.strip()
    # Handle ```json ... ``` blocks
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    # Try direct parse
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback: extract first {...} block
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"No valid JSON found in response: {content[:200]}")


class LLMProvider:
    def __init__(self):
        settings = get_settings()
        self._openai = None

        # Only use DeepSeek V4
        model_name = "deepseek-v4-pro"
        kwargs = {
            "model": model_name,
            "api_key": settings.openai_api_key,
            "temperature": 0.1,
        }
        if settings.openai_api_base:
            kwargs["base_url"] = settings.openai_api_base
        else:
            # Default to DeepSeek API
            kwargs["base_url"] = "https://api.deepseek.com/v1"
        
        self._openai = ChatOpenAI(**kwargs)
        logger.info(f"LLM backend: DeepSeek with model {model_name}")

    async def complete(
        self,
        messages: list[dict],
        response_model: type[BaseModel] | None = None,
    ) -> str | BaseModel:
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
