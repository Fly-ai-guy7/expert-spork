from functools import lru_cache

from app.config import settings
from app.llm.base import LLMClient
from app.llm.claude_client import ClaudeClient
from app.llm.deepseek_client import DeepSeekClient


@lru_cache(maxsize=8)
def get_llm(name: str) -> LLMClient:
    name = name.lower()
    if name in ("claude-opus", "opus", "claude_opus"):
        return ClaudeClient(model=settings.claude_opus_model, name="claude-opus")
    if name in ("claude-sonnet", "sonnet", "claude_sonnet"):
        return ClaudeClient(model=settings.claude_sonnet_model, name="claude-sonnet")
    if name in ("deepseek", "deepseek-chat"):
        return DeepSeekClient(model=settings.deepseek_model, name="deepseek")
    raise ValueError(f"Unknown LLM: {name}")
