from typing import Literal

from openai import AsyncOpenAI

from app.config import settings
from app.llm.base import CacheBlock, LLMClient, LLMResponse


class DeepSeekClient(LLMClient):
    def __init__(self, model: str | None = None, name: str | None = None):
        self.model = model or settings.deepseek_model
        self.name = name or "deepseek"
        self._client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url="https://api.deepseek.com/v1",
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
            system_text = system
        else:
            system_text = "\n\n".join(b.text for b in system)

        chat_messages = [{"role": "system", "content": system_text}, *messages]

        kwargs: dict = {
            "model": self.model,
            "messages": chat_messages,
            "max_tokens": max_tokens,
        }
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}
            if chat_messages and "json" not in chat_messages[0]["content"].lower():
                chat_messages[0]["content"] += "\n\nAlways respond with valid JSON."

        resp = await self._client.chat.completions.create(**kwargs)
        return LLMResponse(
            content=resp.choices[0].message.content or "",
            model=self.model,
            usage={
                "input_tokens": resp.usage.prompt_tokens if resp.usage else 0,
                "output_tokens": resp.usage.completion_tokens if resp.usage else 0,
            },
        )
