"""Request and response schemas for the inference API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class InferenceRequest(BaseModel):
    """Payload sent to the /infer endpoint."""

    text: str = Field(..., min_length=1, max_length=10_000, description="Input text")
    parameters: dict[str, float] = Field(
        default_factory=dict, description="Optional model parameters"
    )


class InferenceResponse(BaseModel):
    """Payload returned from the /infer endpoint."""

    result: str
    model: str
    tokens_used: int = 0


class HealthResponse(BaseModel):
    """Payload returned from the /health endpoint."""

    status: str = "ok"
    version: str
    model_loaded: bool
