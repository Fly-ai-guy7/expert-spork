"""Prometheus metrics + a /metrics endpoint.

Uses a private registry so test runs don't accumulate global state across
app instances. Metric helpers are no-ops-safe: calling them is cheap and
never raises into business logic.
"""
from __future__ import annotations

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)

REGISTRY = CollectorRegistry()

HTTP_REQUEST_SECONDS = Histogram(
    "equalise_http_request_seconds",
    "HTTP request latency",
    labelnames=("method", "path", "status"),
    registry=REGISTRY,
)

LLM_TOKENS = Counter(
    "equalise_llm_tokens_total",
    "LLM tokens consumed",
    labelnames=("model", "kind"),  # kind: input | output | cache_read | cache_creation
    registry=REGISTRY,
)

LLM_CALLS = Counter(
    "equalise_llm_calls_total",
    "LLM calls by provider and outcome",
    labelnames=("provider", "outcome"),  # outcome: success | failure
    registry=REGISTRY,
)

PIPELINE_SECONDS = Histogram(
    "equalise_pipeline_duration_seconds",
    "End-to-end orchestrator pipeline duration",
    registry=REGISTRY,
)

HALLUCINATED_CITATIONS = Counter(
    "equalise_hallucinated_citations_total",
    "Citations flagged as unverified against the corpus",
    registry=REGISTRY,
)


def record_llm_usage(provider: str, model: str, usage: dict) -> None:
    LLM_CALLS.labels(provider=provider, outcome="success").inc()
    mapping = {
        "input": "input_tokens",
        "output": "output_tokens",
        "cache_read": "cache_read_input_tokens",
        "cache_creation": "cache_creation_input_tokens",
    }
    for kind, key in mapping.items():
        val = usage.get(key)
        if val:
            LLM_TOKENS.labels(model=model, kind=kind).inc(val)


def record_llm_failure(provider: str) -> None:
    LLM_CALLS.labels(provider=provider, outcome="failure").inc()


def record_hallucinations(n: int) -> None:
    if n > 0:
        HALLUCINATED_CITATIONS.inc(n)


def render_latest() -> tuple[bytes, str]:
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST
