"""LLM resilience: retry, circuit breaker, provider fallback.

Exercises the resilience layer in isolation with fake inner clients, plus
the factory's fallback routing when a provider's circuit is open.
"""
from __future__ import annotations

import httpx
import pytest

from app.llm.base import CacheBlock, LLMClient, LLMResponse
from app.llm.resilience import CircuitBreaker, CircuitOpenError, ResilientLLMClient


class _FlakyClient(LLMClient):
    """Fails `fail_times` with a retryable error, then succeeds."""

    def __init__(self, fail_times: int, exc: BaseException | None = None):
        self.name = "flaky"
        self.model = "flaky-model"
        self._fail_times = fail_times
        self._calls = 0
        self._exc = exc or httpx.ConnectTimeout("boom")

    async def complete(self, system, messages, max_tokens=4096, response_format="text"):
        self._calls += 1
        if self._calls <= self._fail_times:
            raise self._exc
        return LLMResponse(content="ok", model=self.model, usage={"input_tokens": 1, "output_tokens": 2})


def _resilient(inner, breaker=None, max_retries=3, **kw):
    breaker = breaker or CircuitBreaker(threshold=5, cooldown=60)
    return ResilientLLMClient(inner, breaker=breaker, max_retries=max_retries, **kw)


async def test_retry_then_success():
    client = _resilient(_FlakyClient(fail_times=2), max_retries=3)
    resp = await client.complete("sys", [{"role": "user", "content": "hi"}])
    assert resp.content == "ok"


async def test_retry_exhausted_reraises():
    client = _resilient(_FlakyClient(fail_times=5), max_retries=3)
    with pytest.raises(httpx.ConnectTimeout):
        await client.complete("sys", [{"role": "user", "content": "hi"}])


async def test_non_retryable_error_not_retried():
    class _BadClient(LLMClient):
        name = "bad"
        model = "bad"
        calls = 0

        async def complete(self, *a, **k):
            type(self).calls += 1
            raise ValueError("non-retryable")

    inner = _BadClient()
    client = _resilient(inner, max_retries=3)
    with pytest.raises(ValueError, match="non-retryable"):
        await client.complete("sys", [{"role": "user", "content": "hi"}])
    assert inner.calls == 1, "non-retryable error should not be retried"


async def test_circuit_opens_after_threshold():
    breaker = CircuitBreaker(threshold=2, cooldown=60)
    # Each call fails all retries → one failure recorded per .complete()
    client = _resilient(_FlakyClient(fail_times=99), breaker=breaker, max_retries=1)

    for _ in range(2):
        with pytest.raises(httpx.ConnectTimeout):
            await client.complete("sys", [{"role": "user", "content": "x"}])

    assert breaker.is_open("flaky")
    # Next call short-circuits without touching the inner client
    with pytest.raises(CircuitOpenError):
        await client.complete("sys", [{"role": "user", "content": "x"}])


def test_circuit_recovers_after_cooldown():
    breaker = CircuitBreaker(threshold=1, cooldown=0)  # cooldown 0 → immediate half-open
    breaker.record_failure("p")
    # opened_until = now + 0, so is_open sees elapsed and resets
    assert breaker.is_open("p") is False


def test_success_resets_failures():
    breaker = CircuitBreaker(threshold=3, cooldown=60)
    breaker.record_failure("p")
    breaker.record_failure("p")
    breaker.record_success("p")
    breaker.record_failure("p")
    # Only 1 failure since reset → still closed
    assert breaker.is_open("p") is False


async def test_usage_and_failure_callbacks_fire():
    usage_calls = []
    failure_calls = []
    ok = _resilient(
        _FlakyClient(fail_times=0),
        on_usage=lambda name, model, usage: usage_calls.append((name, model, usage)),
        on_failure=lambda name: failure_calls.append(name),
    )
    await ok.complete("sys", [{"role": "user", "content": "x"}])
    assert usage_calls and usage_calls[0][0] == "flaky"
    assert failure_calls == []

    breaker = CircuitBreaker(threshold=10, cooldown=60)
    bad = _resilient(
        _FlakyClient(fail_times=99), breaker=breaker, max_retries=1,
        on_failure=lambda name: failure_calls.append(name),
    )
    with pytest.raises(httpx.ConnectTimeout):
        await bad.complete("sys", [{"role": "user", "content": "x"}])
    assert failure_calls == ["flaky"]


def test_factory_routes_to_fallback_when_circuit_open(monkeypatch):
    from app.config import settings
    from app.llm import factory

    monkeypatch.setattr(settings, "anthropic_api_key", "dummy")
    monkeypatch.setattr(settings, "deepseek_api_key", "dummy")
    factory._build.cache_clear()
    factory._breaker._state.clear()

    # Normal: claude-opus resolves to a claude-opus-backed client
    assert factory.get_llm("claude-opus").name == "claude-opus"

    # Trip the claude-opus breaker
    for _ in range(settings.llm_circuit_threshold):
        factory._breaker.record_failure("claude-opus")
    assert factory._breaker.is_open("claude-opus")

    # Now claude-opus requests route to the deepseek fallback
    assert factory.get_llm("claude-opus").name == "deepseek"

    factory._build.cache_clear()
    factory._breaker._state.clear()
