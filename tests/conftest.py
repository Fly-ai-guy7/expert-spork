"""Shared fixtures for the test suite."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from httpx import ASGITransport, AsyncClient

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

from expert_spork.main import app
from expert_spork.ml.engine import engine


@pytest.fixture(autouse=True)
async def _load_engine() -> AsyncIterator[None]:
    """Ensure the inference engine is loaded for every test."""
    if not engine.is_loaded:
        await engine.load()
    yield


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Async HTTP client wired to the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
