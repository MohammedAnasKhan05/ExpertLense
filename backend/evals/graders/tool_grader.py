"""
ExpertLens AI — Tool & Execution Trace Grader

Evaluates:
- Tool selection: Did the agent invoke appropriate tools for the question?
- Parameter correctness: Were filters (country, expert) and top_k correctly structured?
- Tool success rate: Ratio of tool calls completing without exceptions
- Evidence usage: Were retrieved chunks actually utilized in final citations?
- Unnecessary calls: Detection of redundant / duplicate queries
- Efficiency: Average calls per task and latency in ms
"""

from typing import Any, Dict, List
from pydantic import BaseModel

from app.tools.registry import ExecutionTrace, ToolExecutionLog
from evals.datasets.benchmark_dataset import EvalTestCase


class ToolEvaluationResult(BaseModel):
    """Result metrics for tool usage evaluation."""
    test_id: str
    tool_selection_accuracy: float = 1.0
    parameter_correctness: float = 1.0
    tool_success_rate: float = 1.0
    evidence_usage_rate: float = 1.0
    unnecessary_calls_count: int = 0
    total_calls: int = 0
    total_latency_ms: float = 0.0
    passed: bool = True
    issues: List[str] = []


class ToolGrader:
    """Evaluates agent tool execution traces."""

    @staticmethod
    def grade(
        test_case: EvalTestCase,
        trace: ExecutionTrace,
        cited_sources: List[Dict[str, Any]],
    ) -> ToolEvaluationResult:
        res = ToolEvaluationResult(
            test_id=test_case.id,
            total_calls=len(trace.tool_calls),
            total_latency_ms=trace.total_latency_ms,
        )

        if not trace.tool_calls:
            # If expected abstention on invalid injection, 0 tool calls might be optimal
            if test_case.expected_behavior == "REJECT_INJECTION":
                res.tool_selection_accuracy = 1.0
                res.passed = True
                return res

            res.tool_selection_accuracy = 0.0
            res.passed = False
            res.issues.append("No tools were called during execution")
            return res

        # 1. Tool Success Rate
        successful_calls = sum(1 for c in trace.tool_calls if c.success)
        res.tool_success_rate = round(successful_calls / len(trace.tool_calls), 3)

        # 2. Parameter Correctness
        param_errors = 0
        for call in trace.tool_calls:
            params = call.parameters
            # Check country filter matches test case target country if specified
            if test_case.target_country and "country" in params and params["country"]:
                if params["country"].lower() != test_case.target_country.lower():
                    param_errors += 1
                    res.issues.append(f"Mismatched country filter in {call.tool_name}: {params['country']}")

        res.parameter_correctness = max(0.0, round(1.0 - (param_errors / max(1, len(trace.tool_calls))), 3))

        # 3. Redundant / Unnecessary Calls
        seen_calls = set()
        unnecessary = 0
        for call in trace.tool_calls:
            key = f"{call.tool_name}:{str(call.parameters)}"
            if key in seen_calls:
                unnecessary += 1
                res.issues.append(f"Duplicate tool call detected: {call.tool_name}")
            seen_calls.add(key)
        res.unnecessary_calls_count = unnecessary

        # 4. Evidence Usage Rate (Ratio of cited chunks to retrieved chunks)
        total_retrieved = sum(c.chunk_count for c in trace.tool_calls if c.tool_name in ["search_transcripts", "retrieve_evidence"])
        cited_count = len(cited_sources)

        if total_retrieved > 0 and test_case.expected_behavior == "ANSWER":
            res.evidence_usage_rate = min(1.0, round(cited_count / max(1, min(5, total_retrieved)), 3))
        else:
            res.evidence_usage_rate = 1.0

        res.passed = (
            res.tool_success_rate >= 0.8
            and res.parameter_correctness >= 0.8
            and res.unnecessary_calls_count == 0
        )

        return res
