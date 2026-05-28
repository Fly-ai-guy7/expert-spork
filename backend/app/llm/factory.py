import logging
from functools import lru_cache

from app.config import settings
from app.llm.base import LLMClient
from app.llm.claude_client import ClaudeClient
from app.llm.deepseek_client import DeepSeekClient
from app.llm.resilience import CircuitBreaker, ResilientLLMClient

logger = logging.getLogger(__name__)

_breaker = CircuitBreaker(
    threshold=settings.llm_circuit_threshold,
    cooldown=settings.llm_circuit_cooldown_seconds,
)

# When a provider's circuit is open, route to the cross-LLM alternate so the
# debate keeps running (degraded but available). Sonnet falls back to deepseek.
_FALLBACK = {
    "claude-opus": "deepseek",
    "claude-sonnet": "deepseek",
    "deepseek": "claude-opus",
}

_ALIASES = {
    "claude-opus": "claude-opus",
    "opus": "claude-opus",
    "claude_opus": "claude-opus",
    "claude-sonnet": "claude-sonnet",
    "sonnet": "claude-sonnet",
    "claude_sonnet": "claude-sonnet",
    "deepseek": "deepseek",
    "deepseek-chat": "deepseek",
}


def _canonical(name: str) -> str:
    canon = _ALIASES.get(name.lower())
    if canon is None:
        raise ValueError(f"Unknown LLM: {name}")
    return canon


def _usage_callback(provider: str, model: str, usage: dict) -> None:
    # Imported lazily so the LLM layer doesn't hard-depend on observability.
    try:
        from app.observability.metrics import record_llm_usage

        record_llm_usage(provider, model, usage)
    except Exception:  # noqa: BLE001
        logger.debug("metrics record failed", exc_info=True)


def _failure_callback(provider: str) -> None:
    try:
        from app.observability.metrics import record_llm_failure

        record_llm_failure(provider)
    except Exception:  # noqa: BLE001
        logger.debug("metrics failure record failed", exc_info=True)


@lru_cache(maxsize=8)
def _build(canonical: str) -> ResilientLLMClient:
    if canonical == "claude-opus":
        inner: LLMClient = ClaudeClient(model=settings.claude_opus_model, name="claude-opus")
    elif canonical == "claude-sonnet":
        inner = ClaudeClient(model=settings.claude_sonnet_model, name="claude-sonnet")
    elif canonical == "deepseek":
        inner = DeepSeekClient(model=settings.deepseek_model, name="deepseek")
    else:  # pragma: no cover — _canonical guards this
        raise ValueError(f"Unknown LLM: {canonical}")
    return ResilientLLMClient(
        inner,
        breaker=_breaker,
        max_retries=settings.llm_max_retries,
        on_usage=_usage_callback,
        on_failure=_failure_callback,
    )


def get_llm(name: str) -> LLMClient:
    """Return a resilient client, routing to the fallback provider if the
    requested provider's circuit is open. Routing is evaluated per call;
    the underlying clients are cached."""
    canonical = _canonical(name)
    if _breaker.is_open(canonical):
        alt = _FALLBACK.get(canonical)
        if alt and not _breaker.is_open(alt):
            logger.warning("LLM circuit open for %s; routing to %s", canonical, alt)
            canonical = alt
    return _build(canonical)
