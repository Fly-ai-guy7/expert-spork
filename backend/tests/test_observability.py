"""Observability: /metrics endpoint, metric helpers, structlog setup."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import create_app
from app.observability import metrics
from app.observability.logging import get_logger, request_id_var, setup_logging


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    def _override():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = _override
    yield TestClient(app)
    engine.dispose()


def test_metrics_endpoint_exposes_prometheus_text(client):
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "text/plain" in r.headers["content-type"]
    # Our custom metric families should be present in the exposition.
    body = r.text
    assert "equalise_http_request_seconds" in body
    assert "equalise_llm_tokens_total" in body or "equalise_llm_calls_total" in body


def test_metrics_endpoint_is_unauthenticated(client):
    # Scrapers must reach it without a bearer token.
    assert client.get("/metrics").status_code == 200


def test_request_id_header_round_trips(client):
    r = client.get("/health", headers={"X-Request-ID": "abc-123"})
    assert r.headers.get("X-Request-ID") == "abc-123"


def test_request_id_generated_when_absent(client):
    r = client.get("/health")
    assert r.headers.get("X-Request-ID")  # some generated id


def test_record_llm_usage_increments_counters():
    before = metrics.LLM_TOKENS.labels(model="m", kind="input")._value.get()
    metrics.record_llm_usage("claude-opus", "m", {
        "input_tokens": 10, "output_tokens": 5,
        "cache_read_input_tokens": 3, "cache_creation_input_tokens": 0,
    })
    after = metrics.LLM_TOKENS.labels(model="m", kind="input")._value.get()
    assert after - before == 10
    assert metrics.LLM_TOKENS.labels(model="m", kind="cache_read")._value.get() >= 3


def test_record_hallucinations_counter():
    before = metrics.HALLUCINATED_CITATIONS._value.get()
    metrics.record_hallucinations(2)
    metrics.record_hallucinations(0)  # no-op
    after = metrics.HALLUCINATED_CITATIONS._value.get()
    assert after - before == 2


def test_setup_logging_and_request_id_binding():
    setup_logging(level="INFO", json_logs=True)
    log = get_logger("test")
    token = request_id_var.set("req-xyz")
    try:
        # Should not raise; structured event emitted to stdout.
        log.info("hello", foo="bar")
    finally:
        request_id_var.reset(token)
