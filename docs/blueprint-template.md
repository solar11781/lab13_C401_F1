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
- EVIDENCE_TRACE_WATERFALL_SCREENSHOT: ![EVIDENCE_TRACE_WATERFALL_SCREENSHOT](/screenshots/evidence_trace_waterfall.png)
- TRACE_WATERFALL_EXPLANATION: Trace này thể hiện quá trình xử lý một request trong pipeline của agent, trong đó span chính agent_reasoning_chain đại diện cho toàn bộ luồng xử lý và span con knowledge_retrieval thực hiện bước truy xuất tài liệu. Metadata cho thấy doc_count = 1, nghĩa là đã truy xuất được một tài liệu, và độ trễ gần như bằng 0 cho thấy bước này không phải là nút thắt hiệu năng. Cấu trúc này giúp quan sát rõ các thành phần trong hệ thống và hỗ trợ việc debug cũng như phân tích hiệu năng.

### 3.2 Dashboard & SLOs

- [DASHBOARD_6_PANELS_SCREENSHOT]:
  screenshots/dashboard_1.png
  screenshots/dashboard_2.png
  screenshots/dashboard_3.png
  screenshots/dashboard_4.png
- [SLO_TABLE]:
  | SLI | Target | Window | Current Value |
  |---|---:|---|---:|
  | Latency P95 | < 2500ms | 28d | |
  | Error Rate | < 2% | 28d | |
  | Cost Budget | < $3.0/day | 28d | |
  | Average Quality Score | > 0.85 | 28d | |

### 3.3 Alerts & Runbook

- ALERT_RULES_SCREENSHOT: ![ALERT_RULES](/screenshots/alert_rules.png)
- SAMPLE_RUNBOOK_LINK: https://github.com/solar11781/Lab13-Observability/blob/main/docs/alerts.md

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

**TASKS_COMPLETED:**

- Update PII in the pii.py file and modify the logging code in logging_config.py
  **EVIDENCE_LINK:**
- https://github.com/solar11781/Lab13-Observability/commit/ccb27c7be72e2b7569d84e1ba676452c0e258d36
- https://github.com/solar11781/Lab13-Observability/commit/6b1fe1d8ac08fc5a76cec3fecb219a16c526fca7
- https://github.com/solar11781/Lab13-Observability/commit/5e945280fd0a1783a906a6dd604d6c994abddcd0
- https://github.com/solar11781/Lab13-Observability/commit/ee4991f97fbed14bffab61f033bf98cc257381e9

### Trương Minh Sơn

**TASKS_COMPLETED:**

- Implemented a robust observability pipeline featuring Langfuse tracing, automated PII scrubbing for logs and traces, and a comprehensive banking-specific test suite to monitor AI agent performance and security, Successfully implement waterfall traces
  **EVIDENCE_LINK:**
- Correlation ID Tracking: [https://github.com/solar11781/Lab13-Observability/blob/main/app/middleware.py](https://github.com/solar11781/Lab13-Observability/blob/main/app/middleware.py)
- Langfuse Integration: [https://github.com/solar11781/Lab13-Observability/blob/main/app/tracing.py](https://github.com/solar11781/Lab13-Observability/blob/main/app/tracing.py)
- Structured Logging and PII Scrubbing: [https://github.com/solar11781/Lab13-Observability/blob/main/app/logging_config.py](https://github.com/solar11781/Lab13-Observability/blob/main/app/logging_config.py)
- Banking Corpus and RAG Knowledge: [https://github.com/solar11781/Lab13-Observability/blob/main/app/mock_rag.py](https://github.com/solar11781/Lab13-Observability/blob/main/app/mock_rag.py)
- Stress Test Scenarios (200 Queries): [https://github.com/solar11781/Lab13-Observability/blob/main/data/bank_sample_queries_200.jsonl](https://github.com/solar11781/Lab13-Observability/blob/main/data/bank_sample_queries_200.jsonl)
- Quality Evaluation Ground Truth: [https://github.com/solar11781/Lab13-Observability/blob/main/data/bank_expected_answers_200.jsonl](https://github.com/solar11781/Lab13-Observability/blob/main/data/bank_expected_answers_200.jsonl)

### Nguyễn Phạm Trà My

**TASKS_COMPLETED**

- Xây dựng **SLO (Service Level Objectives)** trong `config/slo.yaml`:
  - Xác định các SLI chính: latency_p95, error_rate, cost_budget, quality_score
  - Thiết lập target phù hợp với hệ thống chatbot ngân hàng
  - Điền current value dựa trên số liệu thực tế từ metrics và load test

- Cấu hình **Alert Rules** trong `config/alert_rules.yaml`:
  - Thiết lập các alert quan trọng:
    - high_latency_p95
    - high_error_rate
    - cost_budget_spike
    - quality_degradation
  - Định nghĩa condition rõ ràng (threshold + duration)
  - Gán severity (P1/P2) và runbook cho từng alert

- Kiểm tra alert hoạt động bằng cách:
  - Inject các scenario: rag_slow, tool_fail, cost_spike
  - Quan sát metrics thay đổi và đảm bảo alert trigger đúng

- Đảm bảo SLO và alert liên kết chặt chẽ:
  - Alert được thiết kế trực tiếp dựa trên các SLI trong SLO
  - Hệ thống có khả năng phát hiện và cảnh báo khi vi phạm SLO
- [EVIDENCE_LINK]:
- https://github.com/solar11781/lab13_C401_F1/blob/main/config/alert_rules.yaml
- https://github.com/solar11781/lab13_C401_F1/blob/main/config/slo.yaml

### Bùi Trần Gia Bảo

**TASKS_COMPLETED:**

- Executed and validated all incident scenarios (rag_slow, tool_fail, cost_spike) using load_test.py and inject_incident.py, confirming expected system behaviors (latency increase, error spikes, cost increase).
- Created domain-specific banking test datasets (200 queries + expected answers) to simulate realistic chatbot usage.
- Developed adversarial test cases (PII injection, fraud attempts, prompt injection, malformed inputs) to evaluate system robustness and security.
- Verified system stability under edge cases (no crashes, consistent responses, proper error handling).
- Collected metrics and validated system performance using /metrics endpoint (latency, cost, tokens, error breakdown).

**EVIDENCE_LINK:**

- https://github.com/solar11781/Lab13-Observability/commit/d914cc085acb24c40f2216cf371ee11563002e43
- https://github.com/solar11781/Lab13-Observability/commit/34b13221128d333f103a501b6baf5f03d4d70745
- https://github.com/solar11781/Lab13-Observability/commit/36c400cb66ea12ca3643839d59597fea49e55e72
- https://github.com/solar11781/Lab13-Observability/commit/c25b9490ecde945cd375508042769ceeaa40961d
- https://github.com/solar11781/Lab13-Observability/commit/e4a841aafa02c79b006afa1f358850b41c7d2193

### Mạc Phương Nga

**TASKS_COMPLETED:**
- Update `app/agent.py` và hoàn thành dashboard - `app/dashboard.html`
**EVIDENCE_LINK:**
- https://github.com/solar11781/Lab13-Observability/commit/68a62967f06055804fed5ac83f3409a6fb024ffe
- https://github.com/solar11781/Lab13-Observability/commit/9b0b1f59fc203689b08ecf536451fb21cde1b120
- https://github.com/solar11781/Lab13-Observability/commit/4d0cc3335c23d0c8336425eaf18e4491aa06b2e1
- https://github.com/solar11781/Lab13-Observability/commit/87614f6706f695d06f3b78796870b26f4c7a2c1a

### Lại Gia Khánh

**TASKS_COMPLETED:**

- Hoàn thành team report (blueprint-template.md) và chuẩn bị mock-debug-qa.md.
  **EVIDENCE_LINK:**
- https://github.com/solar11781/Lab13-Observability/commit/aec716cf600567eee892c45fb47a312020554dab
- https://github.com/solar11781/Lab13-Observability/commit/1c07379e260a0dc7b7011e2731790b999e9f06e3
- https://github.com/solar11781/Lab13-Observability/commit/4f373854699921d7e22d23eebb002391611bf0c9
- https://github.com/solar11781/Lab13-Observability/commit/c7d77675f41804cb9150a10c38f4d21d93f31f8a

---

## 6. Bonus Items (Optional)

- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
