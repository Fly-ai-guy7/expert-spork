"""Tests for the /infer endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient


async def test_infer_returns_result(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/infer", json={"text": "Hello Hurghada"})
    assert resp.status_code == 200
    data = resp.json()
    assert "result" in data
    assert data["model"] == "default"
    assert data["tokens_used"] > 0


async def test_infer_rejects_empty_text(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/infer", json={"text": ""})
    assert resp.status_code == 422


async def test_infer_with_parameters(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/infer",
        json={"text": "test input", "parameters": {"temperature": 0.7}},
    )
    assert resp.status_code == 200
    assert "result" in resp.json()
