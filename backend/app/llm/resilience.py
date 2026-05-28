"""Resilience layer for LLM calls: retry, timeout, circuit breaker.

Wraps any LLMClient. Transient failures (429, 5xx, timeouts, connection
errors) are retried with exponential backoff + jitter. Repeated failures trip
a per-provider circuit breaker; the factory then routes to the alternate
provider until the breaker cools down.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Literal

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from app.llm.base import CacheBlock, LLMClient, LLMResponse

logger = logging.getLogger(__name__)


class CircuitOpenError(RuntimeError):
    """Raised when a provider's circuit breaker is open."""


def retryable_exceptions() -> tuple[type[BaseException], ...]:
    """Transient error types worth retrying — gathered defensively so a
    missing SDK doesn't break import."""
    excs: list[type[BaseException]] = [httpx.TimeoutException, httpx.NetworkError]
    try:
        import anthropic

        excs += [
            anthropic.RateLimitError,
            anthropic.APITimeoutError,
            anthropic.APIConnectionError,
            anthropic.InternalServerError,
        ]
    except Exception:  # noqa: BLE001
        pass
    try:
        import openai

        excs += [
            openai.RateLimitError,
            openai.APITimeoutError,
            openai.APIConnectionError,
            openai.InternalServerError,
        ]
    except Exception:  # noqa: BLE001
        pass
    return tuple(excs)


@dataclass
class _BreakerState:
    failures: int = 0
    opened_until: float = 0.0


class CircuitBreaker:
    """In-process, per-provider breaker. Good enough for a single worker;
    Tier 1 swaps the backing store for Redis so it's shared across workers."""

    def __init__(self, threshold: int, cooldown: float):
        self.threshold = threshold
        self.cooldown = cooldown
        self._state: dict[str, _BreakerState] = {}

    def is_open(self, name: str) -> bool:
        st = self._state.get(name)
        if not st or not st.opened_until:
            return False
        if time.monotonic() >= st.opened_until:
            # Cooldown elapsed — half-open: clear and allow a trial call.
            self._state[name] = _BreakerState()
            return False
        return True

    def record_success(self, name: str) -> None:
        self._state[name] = _BreakerState()

    def record_failure(self, name: str) -> None:
        st = self._state.setdefault(name, _BreakerState())
        st.failures += 1
        if st.failures >= self.threshold:
            st.opened_until = time.monotonic() + self.cooldown
            logger.warning("circuit breaker OPEN for %s (%d failures)", name, st.failures)


class ResilientLLMClient(LLMClient):
    """Decorates an inner client with retry + circuit-breaker accounting."""

    def __init__(
        self,
        inner: LLMClient,
        breaker: CircuitBreaker,
        max_retries: int,
        on_usage=None,
        on_failure=None,
    ):
        self._inner = inner
        self.name = inner.name
        self.model = getattr(inner, "model", inner.name)
        self._breaker = breaker
        self._max_retries = max_retries
        self._on_usage = on_usage
        self._on_failure = on_failure

    async def complete(
        self,
        system: str | list[CacheBlock],
        messages: list[dict],
        max_tokens: int = 4096,
        response_format: Literal["text", "json"] = "text",
    ) -> LLMResponse:
        if self._breaker.is_open(self.name):
            raise CircuitOpenError(self.name)

        resp: LLMResponse | None = None
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(self._max_retries),
                wait=wait_exponential_jitter(initial=1, max=10),
                retry=retry_if_exception_type(retryable_exceptions()),
                reraise=True,
            ):
                with attempt:
                    resp = await self._inner.complete(
                        system, messages, max_tokens, response_format
                    )
        except Exception:
            self._breaker.record_failure(self.name)
            if self._on_failure:
                try:
                    self._on_failure(self.name)
                except Exception:  # noqa: BLE001
                    logger.debug("failure callback failed", exc_info=True)
            raise

        self._breaker.record_success(self.name)
        if self._on_usage and resp is not None:
            try:
                self._on_usage(self.name, self.model, resp.usage or {})
            except Exception:  # noqa: BLE001 — metrics must never break a call
                logger.debug("usage callback failed", exc_info=True)
        return resp
