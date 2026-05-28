from typing import Literal

from anthropic import AsyncAnthropic

from app.config import settings
from app.llm.base import CacheBlock, LLMClient, LLMResponse


class ClaudeClient(LLMClient):
    def __init__(self, model: str, name: str | None = None):
        self.model = model
        self.name = name or model
        self._client = AsyncAnthropic(
            api_key=settings.anthropic_api_key,
            timeout=settings.llm_timeout_seconds,
            max_retries=0,  # retries handled by ResilientLLMClient
        )

    async def complete(
        self,
        system: str | list[CacheBlock],
        messages: list[dict],
        max_tokens: int = 4096,
        response_format: Literal["text", "json"] = "text",
    ) -> LLMResponse:
        if isinstance(system, str):
            system_param = system
        else:
            system_param = []
            for block in system:
                entry: dict = {"type": "text", "text": block.text}
                if block.cacheable:
                    entry["cache_control"] = {"type": "ephemeral"}
                system_param.append(entry)

        if response_format == "json":
            messages = list(messages)
            if messages and messages[-1].get("role") == "user":
                messages[-1] = {
                    **messages[-1],
                    "content": messages[-1]["content"]
                    + "\n\nRespond with valid JSON only, no prose.",
                }

        resp = await self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_param,
            messages=messages,
        )

        text_parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
        return LLMResponse(
            content="".join(text_parts),
            model=self.model,
            usage={
                "input_tokens": resp.usage.input_tokens,
                "output_tokens": resp.usage.output_tokens,
                "cache_creation_input_tokens": getattr(
                    resp.usage, "cache_creation_input_tokens", 0
                ),
                "cache_read_input_tokens": getattr(resp.usage, "cache_read_input_tokens", 0),
            },
        )
