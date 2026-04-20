# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- GROUP_NAME: C401-F1
- REPO_URL: https://github.com/solar11781/Lab13-Observability
- MEMBERS:
  - Member A: Lê Duy Anh | Role: Logging & PII
  - Member B: Trương Minh Sơn | Role: Tracing & Enrichment
  - Member C: Nguyễn Phạm Trà My | Role: SLO & Alerts
  - Member D: Bùi Trần Gia Bảo | Role: Load Test & Incident Injection
  - Member E: Mạc Phương Nga | Role: Dashboard & Evidence
  - Member F: Lại Gia Khánh | Role: Report & Demo

---

## 2. Group Performance (Auto-Verified)
- VALIDATE_LOGS_FINAL_SCORE: 100/100
- TOTAL_TRACES_COUNT: 200
- PII_LEAKS_FOUND: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- EVIDENCE_CORRELATION_ID_SCREENSHOT: ![CORRELATION_ID](/screenshots/correlation_id.png)
- EVIDENCE_PII_REDACTION_SCREENSHOT: ![PII_REDACTION](/screenshots/pii_redaction.png)
- EVIDENCE_TRACE_WATERFALL_SCREENSHOT: [Path to image]
- TRACE_WATERFALL_EXPLANATION: (Briefly explain one interesting span in your trace)

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: [Path to image]
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 2500ms | 28d |  |
| Error Rate | < 2% | 28d | |
| Cost Budget | < $3.0/day | 28d | |
| Average Quality Score | < 0.85 | 28d | |

### 3.3 Alerts & Runbook
- ALERT_RULES_SCREENSHOT: ![ALERT RULES](/screenshots/alert_rules.png)
- SAMPLE_RUNBOOK_LINK: [docs/alerts.md#L...]

---

## 4. Incident Response (Group)

- [SCENARIO_NAME]&#58; tool_fail
- [SYMPTOMS_OBSERVED]&#58; All chatbot requests returned HTTP 500 almost immediately during load testing. The load test showed every request failing while the app stayed online, and /metrics showed errors accumulating under RuntimeError.
- [ROOT_CAUSE_PROVED_BY]&#58; Log evidence: `event=request_failed`, `error_type=RuntimeError`, `detail="Vector store timeout"` with correlation IDs such as `req-db7f0d9b`, `req-dec69378`, and `req-57337486`. Code evidence: in `app/mock_rag.py`, when `STATE["tool_fail"]` is enabled, `retrieve()` raises `RuntimeError("Vector store timeout")`, which propagates to `/chat` and is returned as HTTP 500.
- [FIX_ACTION]&#58; Disabled the injected incident using `python scripts/inject_incident.py --scenario tool_fail --disable`, then re-ran load tests to confirm the system returned to normal behavior. We also fixed the tracing fallback in `app/tracing.py` so requests no longer failed with `_DummyContext` span errors before incident analysis.
- [PREVENTIVE_MEASURE]&#58; Add an alert for abnormal error-rate spikes grouped by `error_type`, keep a runbook step to check whether `tool_fail` or other incident toggles are enabled, and add a fallback retrieval path or graceful degradation message instead of returning HTTP 500 for all requests.

---

## 5. Individual Contributions & Evidence

### Lê Duy Anh
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: (Link to specific commit or PR)

### Trương Minh Sơn
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### Nguyễn Phạm Trà My
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### Bùi Trần Gia Bảo
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### Mạc Phương Nga
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### Lại Gia Khánh
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
