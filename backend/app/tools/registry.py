"""
ExpertLens AI — Tool Registry & Execution Tracer

Defines invocable tools and execution tracing for the research agent pipeline.
Logs tool calls, parameters, latency, token usage, retrieved evidence, and errors.
"""

import time
import uuid
import logging
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from app.services.retrieval import retrieve_for_question, get_chunk_with_context
from app.services.quote_validator import validate_quote, normalize_text
from app.vectorstore.chroma import query_chunks

logger = logging.getLogger(__name__)


class ToolExecutionLog(BaseModel):
    """Execution trace entry for a single tool call."""
    call_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    tool_name: str
    parameters: Dict[str, Any]
    result_summary: str = ""
    chunk_count: int = 0
    latency_ms: float = 0.0
    token_usage_est: int = 0
    success: bool = True
    error: Optional[str] = None


class ExecutionTrace(BaseModel):
    """Full execution trace for an agent or retrieval pipeline run."""
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    tool_calls: List[ToolExecutionLog] = Field(default_factory=list)
    total_latency_ms: float = 0.0
    total_token_est: int = 0
    final_answer: str = ""
    citations_count: int = 0
    guardrail_actions: List[str] = Field(default_factory=list)


class ToolTracer:
    """Context manager and recorder for tool execution traces."""

    def __init__(self, question: str = ""):
        self.trace = ExecutionTrace(question=question)
        self._start_time = time.perf_counter()

    def record_call(
        self,
        tool_name: str,
        params: Dict[str, Any],
        result: Any,
        duration_ms: float,
        error: Optional[str] = None,
    ) -> ToolExecutionLog:
        chunk_count = 0
        summary = ""
        tokens = 0

        if isinstance(result, list):
            chunk_count = len(result)
            summary = f"Returned {chunk_count} items"
            # Estimate tokens (~1.3 tokens per word)
            text_len = sum(len(str(item.get("text", item.get("document", "")))) for item in result if isinstance(item, dict))
            tokens = int(text_len / 4)
        elif isinstance(result, dict):
            chunk_count = 1
            summary = f"Result keys: {list(result.keys())}"
            tokens = int(len(str(result)) / 4)
        elif isinstance(result, bool):
            summary = f"Result: {result}"
        else:
            summary = str(result)[:100]

        log = ToolExecutionLog(
            tool_name=tool_name,
            parameters={k: v for k, v in params.items() if not k.startswith("_")},
            result_summary=summary,
            chunk_count=chunk_count,
            latency_ms=round(duration_ms, 2),
            token_usage_est=tokens,
            success=error is None,
            error=error,
        )
        self.trace.tool_calls.append(log)
        return log

    def finalize(self, answer: str = "", citations_count: int = 0) -> ExecutionTrace:
        self.trace.total_latency_ms = round((time.perf_counter() - self._start_time) * 1000, 2)
        self.trace.total_token_est = sum(c.token_usage_est for c in self.trace.tool_calls)
        self.trace.final_answer = answer
        self.trace.citations_count = citations_count
        return self.trace


# ---------------------------------------------------------------------------
# Invocable Tools
# ---------------------------------------------------------------------------

async def tool_search_transcripts(query: str, top_k: int = 5, tracer: Optional[ToolTracer] = None) -> List[Dict[str, Any]]:
    """Search transcript chunks using semantic token similarity."""
    t0 = time.perf_counter()
    err = None
    results = []
    try:
        results = query_chunks(query_text=query, n_results=top_k)
    except Exception as e:
        err = str(e)
        logger.warning(f"tool_search_transcripts failed: {e}")
    finally:
        if tracer:
            tracer.record_call("search_transcripts", {"query": query, "top_k": top_k}, results, (time.perf_counter() - t0) * 1000, err)
    return results


async def tool_retrieve_evidence(
    question: str,
    db: Any,
    country: Optional[str] = None,
    expert_name: Optional[str] = None,
    top_k: int = 5,
    tracer: Optional[ToolTracer] = None,
) -> List[Dict[str, Any]]:
    """Retrieve grounded evidence chunks for a question with optional filters."""
    t0 = time.perf_counter()
    err = None
    chunks = []
    try:
        chunks = await retrieve_for_question(
            question=question,
            db=db,
            country=country,
            expert_name=expert_name,
            top_k=top_k,
        )
    except Exception as e:
        err = str(e)
        logger.warning(f"tool_retrieve_evidence failed: {e}")
    finally:
        if tracer:
            tracer.record_call(
                "retrieve_evidence",
                {"question": question, "country": country, "expert_name": expert_name, "top_k": top_k},
                chunks,
                (time.perf_counter() - t0) * 1000,
                err,
            )
    return chunks


def tool_filter_by_country(chunks: List[Dict[str, Any]], country: str, tracer: Optional[ToolTracer] = None) -> List[Dict[str, Any]]:
    """Filter retrieved chunks by expert country."""
    t0 = time.perf_counter()
    filtered = [c for c in chunks if str(c.get("country", "")).lower() == country.lower()]
    if tracer:
        tracer.record_call("filter_by_country", {"country": country, "input_chunks": len(chunks)}, filtered, (time.perf_counter() - t0) * 1000)
    return filtered


def tool_filter_by_expert(chunks: List[Dict[str, Any]], expert_name: str, tracer: Optional[ToolTracer] = None) -> List[Dict[str, Any]]:
    """Filter retrieved chunks by expert name."""
    t0 = time.perf_counter()
    filtered = [c for c in chunks if expert_name.lower() in str(c.get("expert_name", "")).lower()]
    if tracer:
        tracer.record_call("filter_by_expert", {"expert_name": expert_name, "input_chunks": len(chunks)}, filtered, (time.perf_counter() - t0) * 1000)
    return filtered


async def tool_get_transcript_context(chunk_id: str, db: Any, tracer: Optional[ToolTracer] = None) -> Optional[Dict[str, Any]]:
    """Get rich transcript context surrounding a specific chunk."""
    t0 = time.perf_counter()
    err = None
    res = None
    try:
        res = await get_chunk_with_context(chunk_id=chunk_id, db=db)
    except Exception as e:
        err = str(e)
    finally:
        if tracer:
            tracer.record_call("get_transcript_context", {"chunk_id": chunk_id}, res, (time.perf_counter() - t0) * 1000, err)
    return res


def tool_validate_quote(quote: str, source_text: str, tracer: Optional[ToolTracer] = None) -> bool:
    """Validate that a quote exists in the source text."""
    t0 = time.perf_counter()
    is_valid = validate_quote(quote, source_text)
    if tracer:
        tracer.record_call("validate_quote", {"quote_len": len(quote)}, is_valid, (time.perf_counter() - t0) * 1000)
    return is_valid
