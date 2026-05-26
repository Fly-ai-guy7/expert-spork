from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel


class CacheBlock(BaseModel):
    text: str
    cacheable: bool = True


class LLMResponse(BaseModel):
    content: str
    model: str
    usage: dict | None = None


class LLMClient(ABC):
    name: str

    @abstractmethod
    async def complete(
        self,
        system: str | list[CacheBlock],
        messages: list[dict],
        max_tokens: int = 4096,
        response_format: Literal["text", "json"] = "text",
    ) -> LLMResponse: ...
