"""
ExpertLens AI — Human Review Manager

Handles:
- Exporting evaluation cases to JSON and CSV for human review
- Importing completed reviewer annotations
- Calculating agreement metrics & Cohen's Kappa against automated / LLM graders
"""

import csv
import io
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from evals.human_review.rubric import REVIEWER_LABELS, HUMAN_REVIEW_RUBRIC

logger = logging.getLogger(__name__)


class HumanReviewItem(BaseModel):
    """A single evaluation case formatted for human review."""
    test_id: str
    question: str
    retrieved_evidence: str
    generated_answer: str
    citations: str
    quotes: str
    expected_evidence: str
    reviewer_label: Optional[str] = None  # One of REVIEWER_LABELS
    reviewer_notes: Optional[str] = None
    scores: Dict[str, int] = Field(default_factory=dict)  # rubric criteria -> 1-4
    automated_grade_pass: bool = True


class AgreementReport(BaseModel):
    """Agreement statistics between human reviews and automated graders."""
    total_reviews: int = 0
    raw_agreement_rate: float = 0.0
    cohens_kappa: float = 0.0
    disagreement_cases: List[Dict[str, Any]] = []


class ReviewManager:
    """Manages human review export, import, and agreement scoring."""

    @staticmethod
    def export_to_json(items: List[HumanReviewItem], filepath: Optional[str] = None) -> str:
        """Export evaluation cases to JSON."""
        data = [item.model_dump() for item in items]
        dumped = json.dumps(data, indent=2, ensure_ascii=False)
        if filepath:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(dumped)
        return dumped

    @staticmethod
    def export_to_csv(items: List[HumanReviewItem], filepath: Optional[str] = None) -> str:
        """Export evaluation cases to CSV format."""
        output = io.StringIO()
        fieldnames = [
            "test_id",
            "question",
            "retrieved_evidence",
            "generated_answer",
            "citations",
            "quotes",
            "expected_evidence",
            "reviewer_label",
            "reviewer_notes",
            "accuracy_score",
            "groundedness_score",
            "citation_quality_score",
            "automated_grade_pass",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for item in items:
            writer.writerow({
                "test_id": item.test_id,
                "question": item.question,
                "retrieved_evidence": item.retrieved_evidence,
                "generated_answer": item.generated_answer,
                "citations": item.citations,
                "quotes": item.quotes,
                "expected_evidence": item.expected_evidence,
                "reviewer_label": item.reviewer_label or "",
                "reviewer_notes": item.reviewer_notes or "",
                "accuracy_score": item.scores.get("accuracy", ""),
                "groundedness_score": item.scores.get("groundedness", ""),
                "citation_quality_score": item.scores.get("citation_quality", ""),
                "automated_grade_pass": str(item.automated_grade_pass),
            })

        content = output.getvalue()
        if filepath:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8", newline="") as f:
                f.write(content)
        return content

    @staticmethod
    def calculate_agreement(items: List[HumanReviewItem]) -> AgreementReport:
        """
        Calculate agreement rate and Cohen's Kappa between human labels
        and automated pass/fail results.
        """
        reviewed = [i for i in items if i.reviewer_label]
        if not reviewed:
            return AgreementReport()

        agree_count = 0
        disagreements = []

        # Convert reviewer label to binary pass/fail
        # Pass: "Correct", "Partially Correct"
        # Fail: "Incorrect", "Unsupported", "Hallucinated", "Missing Evidence", "Wrong Citation", "Wrong Quote", "Wrong Context"
        a_pass = 0
        a_fail = 0
        b_pass = 0
        b_fail = 0
        both_pass = 0
        both_fail = 0

        for item in reviewed:
            human_pass = item.reviewer_label in ["Correct", "Partially Correct"]
            auto_pass = item.automated_grade_pass

            if human_pass:
                a_pass += 1
            else:
                a_fail += 1

            if auto_pass:
                b_pass += 1
            else:
                b_fail += 1

            if human_pass == auto_pass:
                agree_count += 1
                if human_pass:
                    both_pass += 1
                else:
                    both_fail += 1
            else:
                disagreements.append({
                    "test_id": item.test_id,
                    "question": item.question,
                    "human_label": item.reviewer_label,
                    "automated_pass": auto_pass,
                    "notes": item.reviewer_notes,
                })

        n = len(reviewed)
        raw_agreement = round(agree_count / n, 3)

        # Cohen's Kappa calculation
        # Po = raw_agreement
        # Pe = P(A=pass)*P(B=pass) + P(A=fail)*P(B=fail)
        p_a_pass = a_pass / n
        p_a_fail = a_fail / n
        p_b_pass = b_pass / n
        p_b_fail = b_fail / n
        pe = (p_a_pass * p_b_pass) + (p_a_fail * p_b_fail)

        kappa = round((raw_agreement - pe) / (1.0 - pe), 3) if pe < 1.0 else 1.0

        return AgreementReport(
            total_reviews=n,
            raw_agreement_rate=raw_agreement,
            cohens_kappa=max(-1.0, min(1.0, kappa)),
            disagreement_cases=disagreements,
        )
