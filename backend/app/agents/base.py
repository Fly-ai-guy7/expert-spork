import json
import uuid
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from app.disclaimer import SYSTEM_DISCLAIMER_PREFIX
from app.i18n import Lang
from app.llm import CacheBlock, LLMClient, get_llm


class AgentContext(BaseModel):
    case_id: uuid.UUID
    lang: Lang = Lang.EN
    case_snapshot: dict = Field(default_factory=dict)
    prior_arguments: list[dict] = Field(default_factory=list)
    statute_block: str = ""
    statute_article_ids: list[str] = Field(default_factory=list)
    extra: dict = Field(default_factory=dict)


class AgentOutput(BaseModel):
    content_ar: str | None = None
    content_en: str | None = None
    citations: list[uuid.UUID] = Field(default_factory=list)
    raw: dict = Field(default_factory=dict)
    llm_used: str = ""


class LegalAgent(ABC):
    name: str
    default_llm: str = "claude-sonnet"

    def __init__(self, llm: str | None = None):
        self._llm_name = llm or self.default_llm

    @property
    def llm(self) -> LLMClient:
        return get_llm(self._llm_name)

    @abstractmethod
    async def run(self, ctx: AgentContext) -> AgentOutput: ...

    def _system(self, body: str, ctx: AgentContext) -> list[CacheBlock]:
        blocks = [CacheBlock(text=SYSTEM_DISCLAIMER_PREFIX + body, cacheable=False)]
        if ctx.statute_block:
            blocks.append(CacheBlock(text=ctx.statute_block, cacheable=True))
        return blocks

    @staticmethod
    def _parse_json(content: str) -> dict[str, Any]:
        content = content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.lower().startswith("json"):
                content = content[4:].lstrip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            if start >= 0 and end > start:
                return json.loads(content[start : end + 1])
            return {}
