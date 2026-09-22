"""
Integration and Unit tests for Evaluation Framework.
"""

import pytest
import asyncio
from evals.datasets.benchmark_dataset import BENCHMARK_DATASET, EvalTestCase
from evals.graders.accuracy_grader import AccuracyGrader
from evals.graders.groundedness_grader import GroundednessGrader
from evals.graders.quote_grader import QuoteGrader
from evals.graders.tool_grader import ToolGrader
from evals.human_review.review_manager import ReviewManager, HumanReviewItem
from evals.ab_testing.experiment_runner import ABExperimentRunner
from app.tools.registry import ToolTracer


def test_benchmark_dataset_integrity():
    assert len(BENCHMARK_DATASET) >= 14
    for tc in BENCHMARK_DATASET:
        assert tc.id.startswith("TC-")
        assert tc.question
        assert tc.expected_behavior in ["ANSWER", "SAFE_ABSTENTION", "REJECT_INJECTION"]


def test_accuracy_grader_perfect_match():
    tc = BENCHMARK_DATASET[0]
    answer = "According to Anna Keller in Germany, nine to eighteen months is common for procurement and clinical leadership."
    sources = [{"expert_name": "Anna Keller", "country": "Germany", "quote": "Nine to eighteen months is common.", "verified": True}]
    res = AccuracyGrader.grade(tc, answer, sources)
    assert res.passed is True
    assert res.overall_accuracy >= 0.85


def test_groundedness_grader_detects_hallucination():
    tc = BENCHMARK_DATASET[0]
    # Injected false statistic "three years"
    answer = "The purchasing decision takes three years."
    sources = []
    chunks = []
    res = GroundednessGrader.grade(tc, answer, sources, chunks)
    assert res.is_hallucinated is True
    assert res.passed is False


def test_quote_grader_exact_and_fail():
    exact_cite = [{"expert_name": "Anna Keller", "timestamp": "06:05", "quote": "Nine to eighteen months is common."}]
    fake_cite = [{"expert_name": "Anna Keller", "timestamp": "00:00", "quote": "We buy robots every single Tuesday for free."}]

    res_pass = QuoteGrader.verify_quotes("T1", exact_cite)
    assert res_pass.passed is True
    assert res_pass.pass_rate == 1.0

    res_fail = QuoteGrader.verify_quotes("T2", fake_cite)
    assert res_fail.passed is False
    assert res_fail.failed_quotes == 1


def test_tool_tracer_and_grader():
    tracer = ToolTracer("Test query")
    tracer.record_call("search_transcripts", {"query": "adoption"}, [{"text": "sample"}], 12.5)
    trace = tracer.finalize("Answer", 1)

    assert len(trace.tool_calls) == 1
    assert trace.tool_calls[0].tool_name == "search_transcripts"

    tc = BENCHMARK_DATASET[0]
    tool_res = ToolGrader.grade(tc, trace, [{"chunk_id": "1"}])
    assert tool_res.tool_success_rate == 1.0


def test_human_review_agreement_calculation():
    items = [
        HumanReviewItem(
            test_id="TC-001",
            question="Q1",
            retrieved_evidence="E1",
            generated_answer="A1",
            citations="C1",
            quotes="Q1",
            expected_evidence="EE1",
            reviewer_label="Correct",
            automated_grade_pass=True,
        ),
        HumanReviewItem(
            test_id="TC-002",
            question="Q2",
            retrieved_evidence="E2",
            generated_answer="A2",
            citations="C2",
            quotes="Q2",
            expected_evidence="EE2",
            reviewer_label="Hallucinated",
            automated_grade_pass=False,
        ),
    ]
    report = ReviewManager.calculate_agreement(items)
    assert report.total_reviews == 2
    assert report.raw_agreement_rate == 1.0
    assert report.cohens_kappa == 1.0
