"""Model loading and inference engine.

Uses a Hugging Face Transformers text-generation pipeline when the ``ml``
extra is installed (``pip install expert-spork[ml]``).  Falls back to a
lightweight stub that echoes input when the ML dependencies are absent or
the model name is ``"default"``.
"""

from __future__ import annotations

import asyncio
from typing import Any

from expert_spork.core.config import settings
from expert_spork.core.logging import get_logger

log = get_logger(__name__)

try:
    from transformers import pipeline as hf_pipeline

    _HAS_TRANSFORMERS = True
except ImportError:  # pragma: no cover
    _HAS_TRANSFORMERS = False


class InferenceEngine:
    """Thin wrapper around model loading and prediction."""

    def __init__(self) -> None:
        self._model_name = settings.model_name
        self._device = settings.model_device
        self._loaded = False
        self._pipeline: Any = None

    async def load(self) -> None:
        """Load the model into memory. Call once at startup."""
        log.info("loading_model", model=self._model_name, device=self._device)
        if _HAS_TRANSFORMERS and self._model_name != "default":
            self._pipeline = hf_pipeline(
                "text-generation",
                model=self._model_name,
                device=self._device,
            )
            log.info("model_ready", model=self._model_name, backend="transformers")
        else:
            if not _HAS_TRANSFORMERS:
                log.warning(
                    "transformers_not_installed",
                    hint="pip install expert-spork[ml]",
                )
            log.info("model_ready", model=self._model_name, backend="stub")
        self._loaded = True

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    async def predict(self, text: str, parameters: dict[str, float] | None = None) -> str:
        """Run inference on input text and return the result."""
        if not self._loaded:
            raise RuntimeError("Model is not loaded — call load() first")
        log.info("inference", input_len=len(text))
        if self._pipeline is not None:
            gen_kwargs: dict[str, Any] = {"max_new_tokens": 200, "do_sample": True}
            if parameters:
                gen_kwargs.update(parameters)
            outputs = await asyncio.to_thread(self._pipeline, text, **gen_kwargs)
            result: str = outputs[0]["generated_text"]
            return result
        return f"[stub] echo: {text[:100]}"


engine = InferenceEngine()
