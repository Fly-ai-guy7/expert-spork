"""ASGI middleware: per-request id + latency metric.

Generates (or honors an inbound X-Request-ID) request id, binds it for
structured logs, echoes it on the response, and records request latency to
Prometheus labeled by method / route template / status.
"""
from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.observability.logging import request_id_var
from app.observability.metrics import HTTP_REQUEST_SECONDS


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex
        token = request_id_var.set(rid)
        start = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["X-Request-ID"] = rid
            return response
        finally:
            elapsed = time.perf_counter() - start
            # Use the matched route template (not the raw path) to keep label
            # cardinality bounded — /api/cases/{case_id}, not a UUID per series.
            route = request.scope.get("route")
            path = getattr(route, "path", request.url.path)
            HTTP_REQUEST_SECONDS.labels(
                method=request.method, path=path, status=str(status)
            ).observe(elapsed)
            request_id_var.reset(token)
