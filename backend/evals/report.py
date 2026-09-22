"""
ExpertLens AI — Evaluation Report Generator

Formats and exports evaluation results to:
- Terminal ASCII / ANSI tables
- Structured JSON reports
- CSV reports for spreadsheets & audits
- Markdown summary reports
"""

import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from evals.graders.classification_grader import ClassificationResult


class TestCaseEvaluationRecord(BaseModel):
    """Full evaluation record for a single test case."""
    test_id: str
    category: str
    question: str
    answer: str
    passed: bool
    accuracy: float
    groundedness: float
    hallucination_rate: float
    citation_coverage: float
    quote_pass_rate: float
    tool_calls_count: int
    latency_ms: float
    failure_types: List[str] = Field(default_factory=list)  # RETRIEVAL_FAILURE, CONTEXT_FAILURE, LLM_FAILURE, PROMPT_FAILURE, CITATION_FAILURE, QUOTE_FAILURE, GUARDRAIL_FAILURE, TOOL_FAILURE


class FullEvaluationReport(BaseModel):
    """Comprehensive evaluation run report."""
    run_id: str
    timestamp: str
    environment: str
    llm_provider: str
    total_test_cases: int = 0
    passed_cases: int = 0
    failed_cases: int = 0
    overall_pass_rate: float = 0.0

    # Summary metric averages
    mean_accuracy: float = 0.0
    mean_groundedness: float = 0.0
    mean_hallucination_rate: float = 0.0
    mean_citation_coverage: float = 0.0
    mean_quote_pass_rate: float = 0.0
    mean_latency_ms: float = 0.0

    # Classification
    classification_metrics: Optional[ClassificationResult] = None

    # Detailed test case records
    records: List[TestCaseEvaluationRecord] = Field(default_factory=list)
    failure_counts: Dict[str, int] = Field(default_factory=dict)


class EvaluationReporter:
    """Generates visual terminal tables, JSON, CSV, and Markdown outputs."""

    @staticmethod
    def print_terminal_summary(report: FullEvaluationReport):
        """Prints a rich, formatted ASCII terminal dashboard."""
        w = 80
        print("\n" + "=" * w)
        print(f"  EXPERTLENS AI — EVALUATION & RELIABILITY DASHBOARD".center(w))
        print("=" * w)
        print(f" Run ID: {report.run_id} | Provider: {report.llm_provider} | Timestamp: {report.timestamp}")
        print("-" * w)

        # Main KPI Scorecard
        pass_pct = f"{report.overall_pass_rate * 100:.1f}%"
        acc_pct = f"{report.mean_accuracy * 100:.1f}%"
        ground_pct = f"{report.mean_groundedness * 100:.1f}%"
        halluc_pct = f"{report.mean_hallucination_rate * 100:.1f}%"
        cit_pct = f"{report.mean_citation_coverage * 100:.1f}%"
        quote_pct = f"{report.mean_quote_pass_rate * 100:.1f}%"

        print(f" {'METRIC':<30} | {'SCORE':<12} | {'STATUS':<15}")
        print("-" * w)
        print(f" {'Overall Benchmark Pass Rate':<30} | {pass_pct:<12} | {'[PASS]' if report.overall_pass_rate >= 0.8 else '[WARN]'}")
        print(f" {'Answer & Fact Accuracy':<30} | {acc_pct:<12} | {'[PASS]' if report.mean_accuracy >= 0.85 else '[WARN]'}")
        print(f" {'Groundedness Score':<30} | {ground_pct:<12} | {'[PASS]' if report.mean_groundedness >= 0.85 else '[WARN]'}")
        print(f" {'Hallucination Rate':<30} | {halluc_pct:<12} | {'[PASS]' if report.mean_hallucination_rate <= 0.05 else '[FAIL]'}")
        print(f" {'Citation Coverage':<30} | {cit_pct:<12} | {'[PASS]' if report.mean_citation_coverage >= 0.80 else '[WARN]'}")
        print(f" {'Quote Deterministic Pass':<30} | {quote_pct:<12} | {'[PASS]' if report.mean_quote_pass_rate >= 0.90 else '[WARN]'}")
        print(f" {'Average Latency':<30} | {f'{report.mean_latency_ms:.1f} ms':<12} | {'[OPTIMAL]'}")

        # Classification KPI
        if report.classification_metrics:
            cm = report.classification_metrics
            print("-" * w)
            print(f" {'TRANSCRIPT CHUNK CLASSIFICATION (10-Class Taxonomy)':<50}")
            print(f" Micro F1: {cm.micro_f1:.3f} | Macro F1: {cm.macro_f1:.3f} | Macro Precision: {cm.macro_precision:.3f} | Macro Recall: {cm.macro_recall:.3f}")

        # Failure Breakdown
        if report.failure_counts:
            print("-" * w)
            print(" FAILURE TYPE BREAKDOWN:")
            for ftype, cnt in report.failure_counts.items():
                print(f"   • {ftype:<25}: {cnt} occurrence(s)")

        # Test Case Details Table
        print("-" * w)
        print(f" {'ID':<8} | {'CATEGORY':<20} | {'ACC':<6} | {'GRD':<6} | {'LATENCY':<9} | {'STATUS'}")
        print("-" * w)
        for r in report.records:
            status_str = "[PASS]" if r.passed else "[FAIL]"
            print(f" {r.test_id:<8} | {r.category:<20} | {r.accuracy:.2f}   | {r.groundedness:.2f}   | {f'{r.latency_ms:.0f}ms':<9} | {status_str}")

        print("=" * w + "\n")

    @staticmethod
    def save_json(report: FullEvaluationReport, filepath: str) -> str:
        """Saves full report to a JSON file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        dumped = json.dumps(report.model_dump(), indent=2, ensure_ascii=False)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(dumped)
        return dumped

    @staticmethod
    def save_csv(report: FullEvaluationReport, filepath: str) -> str:
        """Saves individual test case evaluations to a CSV file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        output = io.StringIO()
        fieldnames = [
            "run_id",
            "test_id",
            "category",
            "question",
            "passed",
            "accuracy",
            "groundedness",
            "hallucination_rate",
            "citation_coverage",
            "quote_pass_rate",
            "tool_calls_count",
            "latency_ms",
            "failure_types",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for r in report.records:
            writer.writerow({
                "run_id": report.run_id,
                "test_id": r.test_id,
                "category": r.category,
                "question": r.question,
                "passed": r.passed,
                "accuracy": r.accuracy,
                "groundedness": r.groundedness,
                "hallucination_rate": r.hallucination_rate,
                "citation_coverage": r.citation_coverage,
                "quote_pass_rate": r.quote_pass_rate,
                "tool_calls_count": r.tool_calls_count,
                "latency_ms": r.latency_ms,
                "failure_types": ";".join(r.failure_types),
            })

        content = output.getvalue()
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        return content
