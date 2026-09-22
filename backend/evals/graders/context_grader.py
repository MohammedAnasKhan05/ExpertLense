"""
ExpertLens AI — Context Understanding Grader

Evaluates:
- Explicit vs implicit reasoning
- Handling of contradictory evidence across markets
- Context-dependent statements
- Ratio of relevant evidence retrieved vs correctly used in reasoning
"""

from typing import Any, Dict, List
from pydantic import BaseModel

from evals.datasets.benchmark_dataset import EvalTestCase


class ContextGradeResult(BaseModel):
    """Result metrics for context understanding."""
    test_id: str
    context_coverage: float = 1.0
    contradiction_handling_score: float = 1.0
    implicit_reasoning_score: float = 1.0
    overall_context_score: float = 1.0
    passed: bool = True
    observations: List[str] = []


class ContextGrader:
    """Evaluates contextual depth and cross-market synthesis."""

    @staticmethod
    def grade(
        test_case: EvalTestCase,
        generated_answer: str,
        retrieved_chunks: List[Dict[str, Any]],
        sources: List[Dict[str, Any]],
    ) -> ContextGradeResult:
        res = ContextGradeResult(test_id=test_case.id)
        lower_ans = generated_answer.lower()

        # 1. Context Coverage: Were key topics from retrieved chunks integrated?
        if retrieved_chunks:
            retrieved_keywords = set()
            for c in retrieved_chunks:
                for word in c.get("text", "").lower().split():
                    if len(word) > 5:
                        retrieved_keywords.add(word)

            ans_words = set(lower_ans.split())
            overlap = len(retrieved_keywords.intersection(ans_words))
            res.context_coverage = min(1.0, round(overlap / max(1, min(15, len(retrieved_keywords))), 3))
        else:
            res.context_coverage = 1.0 if test_case.expected_behavior == "SAFE_ABSTENTION" else 0.5

        # 2. Contradiction & Cross-Market Nuance Check
        if test_case.category == "CONTRADICTORY":
            # Must capture both sides (e.g. France/Germany economics vs UK training)
            has_contrast = any(kw in lower_ans for kw in ["while", "whereas", "differ", "contrast", "in the uk", "in germany", "in france", "however", "both"])
            res.contradiction_handling_score = 1.0 if has_contrast else 0.4
            if not has_contrast:
                res.observations.append("Answer lacks comparative nuance across contrasting viewpoints")
        else:
            res.contradiction_handling_score = 1.0

        # 3. Implicit Reasoning Check
        if test_case.category == "IMPLICIT_CONTEXT":
            facts_found = sum(1 for f in test_case.expected_facts if f.lower() in lower_ans)
            res.implicit_reasoning_score = round(facts_found / max(1, len(test_case.expected_facts)), 3)
        else:
            res.implicit_reasoning_score = 1.0

        res.overall_context_score = round(
            (0.4 * res.context_coverage) + (0.3 * res.contradiction_handling_score) + (0.3 * res.implicit_reasoning_score),
            3,
        )
        res.passed = res.overall_context_score >= 0.70

        return res
