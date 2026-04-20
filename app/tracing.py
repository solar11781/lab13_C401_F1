from __future__ import annotations

import os
from typing import Any

try:
    from langfuse.decorators import observe, langfuse_context
except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator
# Dummy context to avoid import errors when Langfuse keys are not set. This allows the app to run without tracing if the environment variables are missing.
    class _DummySpan:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def update(self, **kwargs):
            return None

# Dummy context to avoid import errors when Langfuse keys are not set. This allows the app to run without tracing if the environment variables are missing.
    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None

        def span(self, name: str = ""):
            return _DummySpan()

    langfuse_context = _DummyContext()

#span name can be used to group related operations together in the tracing system. For example, you might use span names like "llm_generation", "vector_retrieval", or "api_request" to categorize different types of operations in your application. This helps in visualizing and analyzing the traces more effectively in the Langfuse dashboard.
def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
