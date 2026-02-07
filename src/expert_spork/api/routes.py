"""API route definitions."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from expert_spork import __version__
from expert_spork.ml.engine import engine
from expert_spork.schemas.inference import HealthResponse, InferenceRequest, InferenceResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness / readiness probe."""
    return HealthResponse(version=__version__, model_loaded=engine.is_loaded)


@router.post("/infer", response_model=InferenceResponse)
async def infer(body: InferenceRequest) -> InferenceResponse:
    """Run model inference on the provided text."""
    if not engine.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded yet",
        )
    result = await engine.predict(body.text, body.parameters)
    return InferenceResponse(
        result=result,
        model=engine._model_name,
        tokens_used=len(body.text.split()),
    )
