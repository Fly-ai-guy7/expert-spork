"""Worker graceful-shutdown signal handler.

The handler must publish a `worker_draining` event to every active case
channel and never raise — even if the event bus is in a weird state.
"""
from __future__ import annotations

import uuid

from app.services import event_bus
from app.workers.signals import _on_worker_shutting_down


def setup_function(_):
    event_bus.reset()


def teardown_function(_):
    event_bus.reset()


def test_drain_publishes_to_every_active_channel():
    a, b = uuid.uuid4(), uuid.uuid4()
    event_bus.publish(a, {"status": "running", "stage": "started"})
    event_bus.publish(b, {"status": "running", "stage": "evidence_migration_complete"})

    _on_worker_shutting_down(sig="TERM", how="warm", exitcode=0)

    for case_id in (a, b):
        statuses = [(e.get("status"), e.get("stage")) for e in event_bus._channel(case_id).history]
        assert ("running", "worker_draining") in statuses, f"missing drain event for {case_id}"


def test_drain_is_a_noop_when_no_active_channels():
    # Should not raise even with nothing to publish to
    _on_worker_shutting_down(sig="TERM", how="warm", exitcode=0)
    assert event_bus._channels == {}


def test_drain_never_raises_when_event_bus_fails(monkeypatch):
    def _boom(*a, **k):
        raise RuntimeError("simulated bus crash")

    monkeypatch.setattr(event_bus, "publish", _boom)
    # Must swallow the error — the worker is already on its way down.
    _on_worker_shutting_down(sig="TERM", how="warm", exitcode=0)
