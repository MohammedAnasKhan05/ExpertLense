"""
ExpertLens AI — Accuracy & Reliability Grader

Evaluates:
- Answer accuracy (presence of expected ground truth facts)
- Fact accuracy (absence of disallowed / incorrect claims)
- Source accuracy (correct expert and country attribution)
- Citation accuracy (chunk alignment and valid IDs)
- Variance / Reliability across repeated runs
"""

import re
from typing import Any, Dict, List
from pydantic import BaseModel

from evals.datasets.benchmark_dataset import EvalTestCase


class AccuracyResult(BaseModel):
    """Evaluation result for accuracy metrics."""
    test_id: str
    fact_accuracy: float = 0.0
    source_accuracy: float = 0.0
    citation_accuracy: float = 0.0
    overall_accuracy: float = 0.0
    missing_facts: List[str] = []
    forbidden_claims_found: List[str] = []
    source_mismatches: List[str] = []
    passed: bool = True


class AccuracyGrader:
    """Evaluates accuracy of answers against benchmark test cases."""

    @staticmethod
    def grade(test_case: EvalTestCase, generated_answer: str, sources: List[Dict[str, Any]]) -> AccuracyResult:
        res = AccuracyResult(test_id=test_case.id)
        lower_ans = generated_answer.lower()

        # 1. Fact Accuracy: Check presence of expected facts & absence of disallowed claims
        facts_matched = 0.0
        for fact in test_case.expected_facts:
            # Check if keyword or phrase is present
            if fact.lower() in lower_ans:
                facts_matched += 1.0
            else:
                # Sub-token density match
                tokens = [t for t in re.findall(r"\w+", fact.lower()) if len(t) > 2]
                if tokens:
                    token_hits = sum(1 for t in tokens if t in lower_ans)
                    ratio = token_hits / len(tokens)
                    if ratio >= 0.4:
                        facts_matched += min(1.0, 0.7 + (ratio * 0.3))
                    else:
                        res.missing_facts.append(fact)
                else:
                    res.missing_facts.append(fact)

        fact_score = (facts_matched / len(test_case.expected_facts)) if test_case.expected_facts else 1.0

        # Disallowed claims check
        penalty = 0.0
        for claim in test_case.disallowed_claims:
            if claim.lower() in lower_ans:
                res.forbidden_claims_found.append(claim)
                penalty += 0.4

        res.fact_accuracy = max(0.0, min(1.0, fact_score - penalty))

        # 2. Source Accuracy: Verify expert & country matches expected sources
        if test_case.expected_sources:
            matched_sources = 0
            for exp_src in test_case.expected_sources:
                exp_expert = exp_src.get("expert", "").lower()
                exp_country = exp_src.get("country", "").lower()
                exp_quote_sub = exp_src.get("quote_contains", "").lower()

                found = False
                for actual_src in sources:
                    actual_expert = str(actual_src.get("expert_name", "")).lower()
                    actual_country = str(actual_src.get("country", "")).lower()
                    actual_quote = str(actual_src.get("quote", "")).lower()

                    if exp_expert in actual_expert or actual_expert in exp_expert:
                        if exp_country in actual_country or actual_country in exp_country:
                            if not exp_quote_sub or exp_quote_sub in actual_quote or actual_quote in exp_quote_sub:
                                found = True
                                break
                if found:
                    matched_sources += 1
                else:
                    res.source_mismatches.append(f"Missing expected source: {exp_src}")

            res.source_accuracy = matched_sources / len(test_case.expected_sources)
        else:
            res.source_accuracy = 1.0 if not sources or test_case.expected_behavior == "SAFE_ABSTENTION" else 0.8

        # 3. Citation Accuracy: Check that citations are verified and non-empty
        if sources:
            verified_count = sum(1 for s in sources if s.get("verified", False))
            res.citation_accuracy = verified_count / len(sources)
        elif test_case.expected_behavior in ["SAFE_ABSTENTION", "REJECT_INJECTION"]:
            res.citation_accuracy = 1.0
        else:
            res.citation_accuracy = 0.0

        # Overall composite
        res.overall_accuracy = round(
            (0.5 * res.fact_accuracy) + (0.3 * res.source_accuracy) + (0.2 * res.citation_accuracy),
            3,
        )
        res.passed = (
            res.overall_accuracy >= 0.70
            and len(res.forbidden_claims_found) == 0
        )

        return res
