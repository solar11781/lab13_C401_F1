from __future__ import annotations

import os
from typing import Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env when module imports
load_dotenv()


def tracing_enabled() -> bool:
    """Return True when both Langfuse public and secret keys are configured."""
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))


try:
    # Langfuse v4 API
    from langfuse import Langfuse, get_client, propagate_attributes, observe
    from langfuse.span_filter import is_default_export_span

    # Initialize a client when keys are present. Configure to export all spans
    # to avoid dropped intermediate spans during migration/testing.
    if tracing_enabled():
        langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            base_url=os.getenv("LANGFUSE_BASE_URL") or os.getenv("LANGFUSE_HOST"),
            environment=os.getenv("APP_ENV", "dev"),
            release=os.getenv("APP_NAME"),
            flush_interval=float(os.getenv("LANGFUSE_FLUSH_INTERVAL", "1.0")),
            flush_at=int(os.getenv("LANGFUSE_FLUSH_AT", "64")),
            sample_rate=float(os.getenv("LANGFUSE_SAMPLE_RATE", "1.0")),
            # Restore pre-v4 behavior: export all spans so waterfall charts include
            # non-LLM spans during testing. Change this in production if needed.
            should_export_span=lambda _span: True,
        )
    else:
        langfuse = None

    # Provide a convenience client getter
    def get_langfuse_client():
        return get_client()

    # Expose commonly used helpers for the app
    langfuse_client = get_client()
    lf = langfuse_client
    lf_propagate = propagate_attributes
    lf_observe = observe

except Exception:  # pragma: no cover
    # Fallback no-op implementations when Langfuse isn't available
    def lf_observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func

        return decorator


    class _DummySpan:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def update(self, **kwargs: Any):
            pass

        def end(self, **kwargs: Any):
            pass


    class _DummyLangfuse:
        def create_trace_id(self, *, seed: Optional[str] = None) -> str:
            return seed or ""

        def start_as_current_observation(self, *args: Any, **kwargs: Any):
            return _DummySpan()

        def start_observation(self, *args: Any, **kwargs: Any):
            return _DummySpan()

        def propagate_attributes(self, *args: Any, **kwargs: Any):
            class _Ctxt:
                def __enter__(self):
                    return None

                def __exit__(self, exc_type, exc, tb):
                    return False

            return _Ctxt()


    lf = _DummyLangfuse()
    lf_propagate = lf.propagate_attributes
    lf_observe = lf_observe


def score_trace(name: str, value: float, comment: Optional[str] = None) -> None:
    """Send a numeric score to Langfuse for the current trace (no-op when disabled)."""
    if not tracing_enabled():
        return

    try:
        # Use the SDK's score helpers when available
        client = lf
        if hasattr(client, "score_current_trace"):
            client.score_current_trace(name=name, value=value, comment=comment)
    except Exception:
        # Don't raise from tracing helper
        pass


# Export short names used across the app
__all__ = ["tracing_enabled", "lf", "lf_propagate", "lf_observe", "score_trace"]