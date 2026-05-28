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
from starlette.responses import Response

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


# Static security headers applied to every response. CSP is intentionally
# strict for the API; the SPA is served by Caddy which sets its own.
_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        for k, v in _SECURITY_HEADERS.items():
            response.headers.setdefault(k, v)
        return response
