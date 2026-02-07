"""Model loading and inference engine.

Swap in real model logic (e.g. Hugging Face Transformers, ONNX, vLLM)
once the team has selected a model architecture.
"""

from __future__ import annotations

from expert_spork.core.config import settings
from expert_spork.core.logging import get_logger

log = get_logger(__name__)


class InferenceEngine:
    """Thin wrapper around model loading and prediction."""

    def __init__(self) -> None:
        self._model_name = settings.model_name
        self._device = settings.model_device
        self._loaded = False

    async def load(self) -> None:
        """Load the model into memory. Call once at startup."""
        log.info("loading_model", model=self._model_name, device=self._device)
        # TODO: replace with actual model loading
        self._loaded = True
        log.info("model_ready", model=self._model_name)

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    async def predict(self, text: str, parameters: dict[str, float] | None = None) -> str:
        """Run inference on input text and return the result."""
        if not self._loaded:
            raise RuntimeError("Model is not loaded — call load() first")
        # TODO: replace with actual inference
        log.info("inference", input_len=len(text))
        return f"[placeholder] echo: {text[:100]}"


engine = InferenceEngine()
