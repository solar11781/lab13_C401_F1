from __future__ import annotations

import os
from typing import Any, Optional
from dotenv import load_dotenv

# Nạp các biến môi trường từ file .env ngay khi module được load
load_dotenv()

def tracing_enabled() -> bool:
    """Kiểm tra xem các API Keys cần thiết đã được thiết lập chưa."""
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))

try:
    # Thử nạp thư viện Langfuse chính thức
    from langfuse.decorators import observe, langfuse_context
    from langfuse import Langfuse
    
    # Chỉ khởi tạo client chính nếu Keys tồn tại
    if tracing_enabled():
        langfuse = Langfuse()
    else:
        langfuse = None
        
except ImportError:  # pragma: no cover
    # Cơ chế dự phòng (Fallback) nếu môi trường chưa cài đặt thư viện hoặc lỗi import
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    class _DummySpan:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): return False
        def update(self, **kwargs): pass
        def end(self, **kwargs): pass

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None: pass
        def update_current_observation(self, **kwargs: Any) -> None: pass
        def span(self, name: str = ""): return _DummySpan()
        def score(self, **kwargs: Any) -> None: pass

    langfuse_context = _DummyContext()
    langfuse = None

def score_trace(name: str, value: float, comment: Optional[str] = None) -> None:
    """
    Gửi điểm số đánh giá chất lượng (quality score) lên Langfuse.
    Giúp Member B tự động hóa báo cáo Metrics.
    """
    if not tracing_enabled():
        return

    try:
        langfuse_context.score(
            name=name,
            value=value,
            comment=comment
        )
    except Exception:
        # Không raise lỗi ở đây để tránh làm sập luồng chính của Agent
        pass