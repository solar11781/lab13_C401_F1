# Alert Rules and Runbooks

This runbook is written against the current codebase behavior:
- `/metrics` exposes `latency_p95_ms`, `error_rate_pct`, `daily_cost_usd`, `quality_score_avg`, and `pii_leak_count`
- `daily_cost_usd` is currently an alias of cumulative request cost in memory for the current app process, not a true persisted 24-hour rolling total
- `pii_leak_count` increases when the logging scrubber detects raw PII in log payload fields or event text before redaction

## 1. High latency P95
- Severity: P2
- Owner: `team-oncall`
- Type: symptom-based
- Trigger: `latency_p95_ms > 4000 for 10m`
- Signal source:
  - `/metrics -> latency_p95_ms`
  - `response_sent` log lines with high `latency_ms`
  - slow Langfuse traces
- Impact:
  - users experience slow responses
  - SLO for tail latency is at risk or already breached
- First checks:
  1. Open the slowest traces from the last hour.
  2. Compare `knowledge_retrieval` span time vs `llm_generation` span time.
  3. Check whether incident toggle `rag_slow` is enabled.
  4. Confirm whether request volume is unusually high.
- Likely causes:
  - retrieval slowdown
  - prompt growth causing longer generation time
  - overloaded local environment during load test
- Mitigation:
  - truncate long queries
  - switch to fallback retrieval
  - reduce prompt size
  - temporarily lower concurrency during incident handling
- Recovery:
  - `latency_p95_ms` drops below threshold for at least one full alert window
  - new traces show normal retrieval and generation timings
- Evidence to capture:
  - one slow trace screenshot
  - one `/metrics` snapshot before mitigation
  - one `/metrics` snapshot after mitigation

## 2. High error rate
- Severity: P1
- Owner: `team-oncall`
- Type: symptom-based
- Trigger: `error_rate_pct > 5 for 5m`
- Signal source:
  - `/metrics -> error_rate_pct`
  - `/metrics -> error_breakdown`
  - `request_failed` log events with `error_type`
- Impact:
  - users receive failed responses
  - availability and trust drop quickly
- First checks:
  1. Group recent logs by `error_type`.
  2. Inspect one or two failed traces end-to-end.
  3. Check whether the failures come from model, tool, schema, or app code.
  4. Review the most recent code or config change.
- Likely causes:
  - exception in request handling
  - schema mismatch
  - failing dependency or incident toggle
- Mitigation:
  - rollback the latest risky change
  - disable the failing tool or feature path
  - return a guarded fallback response
  - retry with a fallback model if the error is model-specific
- Recovery:
  - `error_rate_pct` stays below 5 for one full alert window
  - `request_failed` spikes stop appearing in logs
- Evidence to capture:
  - dominant `error_type`
  - one failed trace ID
  - fix or rollback action taken

## 3. Cost budget spike
- Severity: P2
- Owner: `finops-owner`
- Type: symptom-based
- Trigger: `daily_cost_usd > 5 for 15m`
- Important note:
  - the current app exposes `daily_cost_usd` as the cumulative in-memory cost for the current app process
  - this is suitable for lab monitoring, but not a true persisted 24-hour rolling total
- Signal source:
  - `/metrics -> daily_cost_usd`
  - `/metrics -> avg_cost_usd`
  - `/metrics -> tokens_in_total` and `tokens_out_total`
  - traces split by feature and model
- Impact:
  - burn rate exceeds budget
  - prompt, routing, or retry behavior may be inefficient
- First checks:
  1. Compare current total cost to the normal session baseline.
  2. Split traces by feature and model.
  3. Compare `tokens_in_total` and `tokens_out_total` growth.
  4. Check whether incident toggle `cost_spike` was enabled.
- Likely causes:
  - prompt explosion
  - routing too many requests to an expensive model
  - retry loop or excessive output tokens
- Mitigation:
  - shorten prompts
  - route simpler requests to a cheaper model
  - add prompt caching
  - cap expensive features until usage stabilizes
- Recovery:
  - cost growth returns near baseline
  - token usage per request falls back to expected range
- Evidence to capture:
  - one cost snapshot
  - token comparison before and after mitigation
  - model routing decision or prompt change

## 4. Quality degradation
- Severity: P1
- Owner: `team-oncall`
- Type: symptom-based
- Trigger: `quality_score_avg < 0.75 for 15m`
- Signal source:
  - `/metrics -> quality_score_avg`
  - traces with weak retrieval context
  - wrong or incomplete answers seen during sample evaluation
- Impact:
  - responses succeed technically but are less useful or less accurate
- First checks:
  1. Inspect recent low-quality responses and compare them with retrieved docs.
  2. Check whether retrieval returned empty or weak context.
  3. Review prompt or model changes.
- Mitigation:
  - restore the last known-good prompt
  - improve retrieval quality
  - route sensitive questions to a stronger model
- Recovery:
  - `quality_score_avg` returns above the desired threshold
  - manual spot checks look normal again

## 5. PII leak detected
- Status: code-backed metric available, not currently enabled in `config/alert_rules.yaml`
- Suggested severity: P1
- Suggested owner: `security-oncall`
- Suggested trigger: `pii_leak_count > 0 for 1m`
- Signal source:
  - `/metrics -> pii_leak_count`
  - log lines where raw user content would have been scrubbed by `scrub_event`
  - PII detectors in `app/pii.py`
- Impact:
  - raw sensitive data may be reaching logs before sanitization is confirmed safe
  - this is a security and compliance incident even if the app still serves responses
- First checks:
  1. Search recent logs for raw email, phone number, CCCD, or card-like strings.
  2. Verify `scrub_event` is active in `app/logging_config.py`.
  3. Identify which payload field carried the sensitive value.
  4. Check whether the event came from request input, response preview, or error detail.
- Mitigation:
  - stop or reduce the affected logging path immediately
  - fix scrubbing logic and redeploy
  - remove leaked local log artifacts and rotate downstream sinks if needed
  - replace raw values with summaries or hashed identifiers only
- Recovery:
  - `pii_leak_count` stops increasing
  - manual review confirms new logs are redacted
- Evidence to capture:
  - one sanitized example log line
  - the code path that leaked the value
  - the redaction fix that closed the issue
