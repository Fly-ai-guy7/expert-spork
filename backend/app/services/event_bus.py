"""Per-case event bus for live pipeline updates.

In-memory pub/sub (Redis-backed in a follow-up). Each case has a small
ring buffer of recent events so a late SSE subscriber doesn't miss history,
plus a list of live asyncio.Queue subscribers for tail-following.

Terminal events (status in {complete, failed, paused}) close the subscriber
stream — the next pipeline phase will publish new events that a reconnecting
client picks up.
"""
from __future__ import annotations

import asyncio
import time
import uuid
from collections import deque
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

HISTORY_PER_CASE = 100
TERMINAL_STATUSES = {"complete", "failed", "paused"}


@dataclass
class _Channel:
    history: deque = field(default_factory=lambda: deque(maxlen=HISTORY_PER_CASE))
    subscribers: list[asyncio.Queue] = field(default_factory=list)


_channels: dict[str, _Channel] = {}


def _channel(case_id: uuid.UUID | str) -> _Channel:
    key = str(case_id)
    ch = _channels.get(key)
    if ch is None:
        ch = _Channel()
        _channels[key] = ch
    return ch


def publish(case_id: uuid.UUID | str, event: dict) -> None:
    """Append to the case's ring buffer + fan out to live subscribers.
    Never raises into the caller."""
    try:
        ch = _channel(case_id)
        payload = {**event, "ts": time.time()}
        ch.history.append(payload)
        for q in list(ch.subscribers):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:  # pragma: no cover
                pass
    except Exception:  # noqa: BLE001 — events must never break the pipeline
        pass


async def subscribe(
    case_id: uuid.UUID | str,
    *,
    replay: bool = True,
    timeout_seconds: float | None = 300.0,
) -> AsyncIterator[dict]:
    """Yield events for `case_id`. Replays history first if requested, then
    tails live events until a terminal status arrives or the timeout elapses."""
    ch = _channel(case_id)
    q: asyncio.Queue = asyncio.Queue()
    ch.subscribers.append(q)
    try:
        if replay:
            for evt in list(ch.history):
                yield evt
                if (evt.get("status") or "").lower() in TERMINAL_STATUSES:
                    return
        while True:
            try:
                evt = (
                    await asyncio.wait_for(q.get(), timeout=timeout_seconds)
                    if timeout_seconds
                    else await q.get()
                )
            except TimeoutError:
                return
            yield evt
            if (evt.get("status") or "").lower() in TERMINAL_STATUSES:
                return
    finally:
        if q in ch.subscribers:
            ch.subscribers.remove(q)


def reset() -> None:
    """Test hook: clear all channel state between tests."""
    _channels.clear()
