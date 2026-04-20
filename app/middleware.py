from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Clear contextvars to avoid leakage between asynchronous requests
        clear_contextvars()

        # 2. Extract x-request-id from headers or generate a new one
        # Using the requested format: req-<8-char-hex>
        correlation_id = request.headers.get("x-request-id")
        if not correlation_id:
            correlation_id = f"req-{uuid.uuid4().hex[:8]}"
        
        # 3. Bind the correlation_id to structlog contextvars
        # Every log emitted during this request will now have this ID
        bind_contextvars(correlation_id=correlation_id)
        
        # 4. Attach to request state for use in route handlers
        request.state.correlation_id = correlation_id
        
        start = time.perf_counter()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate execution time
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        
        # 5. Add the correlation_id and processing time to response headers
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = str(elapsed_ms)
        
        return response