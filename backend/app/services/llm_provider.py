import json
import logging
import re
import time

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel
from zhipuai import ZhipuAI

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
        self._zhipu = None
        self._openai = None
        self._anthropic = None
        self._mode = None  # "zhipu" | "openai_compat" | "openai" | "anthropic"

        if settings.openai_api_base and "bigmodel.cn" in settings.openai_api_base:
            # Zhipu GLM — use official zhipuai SDK
            self._zhipu = ZhipuAI(api_key=settings.openai_api_key)
            self._mode = "zhipu"
            logger.info("LLM backend: Zhipu GLM (official SDK)")

        elif settings.openai_api_key:
            # OpenAI-compatible API (DeepSeek, etc.) — use ChatOpenAI but manual JSON parsing
            is_deepseek = settings.openai_api_base and "deepseek" in settings.openai_api_base
            model_name = "deepseek-chat" if is_deepseek else "gpt-4o"
            kwargs = {
                "model": model_name,
                "api_key": settings.openai_api_key,
                "temperature": 0.1,
            }
            if settings.openai_api_base:
                kwargs["base_url"] = settings.openai_api_base
            self._openai = ChatOpenAI(**kwargs)
            # DeepSeek and other compat providers don't support response_format / tool calling
            self._mode = "openai_compat" if settings.openai_api_base else "openai"
            logger.info(f"LLM backend: {self._mode} with model {model_name}")

        if settings.anthropic_api_key:
            self._anthropic = ChatAnthropic(
                model="claude-sonnet-4-20250514",
                api_key=settings.anthropic_api_key,
                temperature=0.1,
            )
            if self._mode is None:
                self._mode = "anthropic"
                logger.info("LLM backend: Anthropic Claude")

    async def complete(
        self,
        messages: list[dict],
        response_model: type[BaseModel] | None = None,
    ) -> str | BaseModel:
        """Complete a conversation. Returns parsed response_model or raw string."""

        # ── Zhipu GLM (official SDK, synchronous) ─────────────────────────────
        if self._mode == "zhipu" and self._zhipu:
            time.sleep(1)  # rate-limit guard for free tier
            response = self._zhipu.chat.completions.create(
                model="glm-4.7-flash",
                messages=[{"role": m["role"], "content": m["content"]} for m in messages],
                temperature=0.1,
            )
            content = response.choices[0].message.content
            if response_model:
                data = _extract_json(content)
                return response_model(**data)
            return content

        # ── OpenAI-compatible (DeepSeek, etc.) — manual JSON parsing ──────────
        if self._mode == "openai_compat" and self._openai:
            result = await self._openai.ainvoke(messages)
            content = result.content
            if response_model:
                data = _extract_json(content)
                return response_model(**data)
            return content

        # ── Native OpenAI — use structured_output ─────────────────────────────
        if self._mode == "openai" and self._openai:
            if response_model:
                structured = self._openai.with_structured_output(response_model)
                return await structured.ainvoke(messages)
            result = await self._openai.ainvoke(messages)
            return result.content

        # ── Anthropic ─────────────────────────────────────────────────────────
        if self._anthropic:
            if response_model:
                structured = self._anthropic.with_structured_output(response_model)
                return await structured.ainvoke(messages)
            result = await self._anthropic.ainvoke(messages)
            return result.content

        raise RuntimeError(
            "No LLM API key configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY."
        )
