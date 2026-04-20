from __future__ import annotations

import os
import time
from dataclasses import dataclass

from . import metrics
from .mock_llm import FakeLLM
from .mock_rag import retrieve
from .pii import hash_user_id, summarize_text
from .tracing import langfuse_context, observe


@dataclass
class AgentResult:
    answer: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    quality_score: float


class LabAgent:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model
        self.llm = FakeLLM(model=model)

    # Added a descriptive name to the trace decorator
    @observe(name="agent_reasoning_chain")
    def run(self, user_id: str, feature: str, session_id: str, message: str, correlation_id: str = None) -> AgentResult:
        started = time.perf_counter()
        user_hash = hash_user_id(user_id)
        guardrail_reason = metrics.detect_guardrail_reason(message)
        pii_detected = metrics.detect_pii(message)
        
        # 1. Force Trace ID to match Correlation ID
        langfuse_context.update_current_trace(
            id=correlation_id,
            user_id=user_hash,
            session_id=session_id,
            tags=["lab-day-13", feature, self.model, os.getenv("APP_ENV", "dev")],
        )
        
        # 2. Nested Span for RAG Retrieval
        rag_started = time.perf_counter()
        with langfuse_context.span(name="knowledge_retrieval") as rag_span:
            docs = retrieve(message)
            rag_span.update(metadata={"doc_count": len(docs)})
        rag_latency_ms = int((time.perf_counter() - rag_started) * 1000)

        prompt = f"Feature={feature}\nDocs={docs}\nQuestion={message}"
        
        # 3. Nested Span for LLM Generation
        with langfuse_context.span(name="llm_generation") as llm_span:
            response = self.llm.generate(prompt)
            llm_span.update(
                metadata={"model_used": self.model},
                usage={"input": response.usage.input_tokens, "output": response.usage.output_tokens}
            )

        quality_score = self._heuristic_quality(message, response.text, docs)
        latency_ms = int((time.perf_counter() - started) * 1000)
        cost_usd = self._estimate_cost(response.usage.input_tokens, response.usage.output_tokens)
        rag_doc_matched = bool(docs) and "No domain document matched" not in docs[0]
        intent_confidence = 0.55
        if rag_doc_matched:
            intent_confidence += 0.25
        if quality_score >= 0.8:
            intent_confidence += 0.1
        if feature in {"qa", "summary"}:
            intent_confidence += 0.05
        intent_confidence = round(min(0.99, max(0.2, intent_confidence)), 3)
        fallback = not rag_doc_matched

        # 4. Finalize the main observation metrics
        langfuse_context.update_current_observation(
            metadata={
                "doc_count": len(docs), 
                "query_preview": summarize_text(message),
                "quality_score": quality_score,
                "guardrail_reason": guardrail_reason,
            },
            usage_details={"input": response.usage.input_tokens, "output": response.usage.output_tokens},
        )

        metrics.record_request(
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            quality_score=quality_score,
            feature=feature,
            model=self.model,
            user_id_hash=user_hash,
            session_id=session_id,
            message=message,
            rag_latency_ms=rag_latency_ms,
            rag_docs_count=len(docs),
            intent_confidence=intent_confidence,
            fallback=fallback,
            guardrail_reason=guardrail_reason,
            pii_detected=pii_detected,
            pii_masked=True,
        )

        return AgentResult(
            answer=response.text,
            latency_ms=latency_ms,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            cost_usd=cost_usd,
            quality_score=quality_score,
        )

    def _estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        input_cost = (tokens_in / 1_000_000) * 3
        output_cost = (tokens_out / 1_000_000) * 15
        return round(input_cost + output_cost, 6)

    def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
        score = 0.5
        if docs:
            score += 0.2
        if len(answer) > 40:
            score += 0.1
        if question.lower().split()[0:1] and any(token in answer.lower() for token in question.lower().split()[:3]):
            score += 0.1
        if "[REDACTED" in answer:
            score -= 0.2
        return round(max(0.0, min(1.0, score)), 2)
    
