from __future__ import annotations

from collections import Counter
from statistics import mean

REQUEST_LATENCIES: list[int] = []
REQUEST_COSTS: list[float] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
ERRORS: Counter[str] = Counter()
TRAFFIC: int = 0
QUALITY_SCORES: list[float] = []


def record_request(
    latency_ms: int,
    cost_usd: float,
    tokens_in: int,
    tokens_out: int,
    quality_score: float,
    **kwargs
) -> None:
    global TRAFFIC
    TRAFFIC += 1
    REQUEST_LATENCIES.append(latency_ms)
    REQUEST_COSTS.append(cost_usd)
    REQUEST_TOKENS_IN.append(tokens_in)
    REQUEST_TOKENS_OUT.append(tokens_out)
    QUALITY_SCORES.append(quality_score)



def record_error(error_type: str) -> None:
    ERRORS[error_type] += 1



def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])



def snapshot() -> dict:
    return {
        "traffic": TRAFFIC,
        "latency_p50": percentile(REQUEST_LATENCIES, 50),
        "latency_p95": percentile(REQUEST_LATENCIES, 95),
        "latency_p99": percentile(REQUEST_LATENCIES, 99),
        "avg_cost_usd": round(mean(REQUEST_COSTS), 4) if REQUEST_COSTS else 0.0,
        "total_cost_usd": round(sum(REQUEST_COSTS), 4),
        "tokens_in_total": sum(REQUEST_TOKENS_IN),
        "tokens_out_total": sum(REQUEST_TOKENS_OUT),
        "error_breakdown": dict(ERRORS),
        "quality_avg": round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
    }

def detect_guardrail_reason(message: str) -> str:
    """
    Dummy guardrail detection (for lab purposes).
    You can expand this later.
    """
    if not message:
        return "empty_input"

    msg = message.lower()

    # simple examples
    if "account number" in msg or "card number" in msg:
        return "pii_exposure"

    if "hack" in msg or "bypass" in msg:
        return "security_risk"

    return "none"

def detect_pii(message: str) -> list[str]:
    """
    Simple PII detection for banking domain (lab version).
    Returns list of detected PII types.
    """
    if not message:
        return []

    msg = message.lower()
    detected = []

    if any(x in msg for x in ["account number", "stk", "số tài khoản"]):
        detected.append("account_number")

    if any(x in msg for x in ["card number", "credit card", "thẻ"]):
        detected.append("card_number")

    if any(x in msg for x in ["cccd", "cmnd", "id number"]):
        detected.append("national_id")

    if any(x in msg for x in ["otp", "password", "pin"]):
        detected.append("credential")

    return detected

