"""
ExpertLens AI — Human Review Rubrics

Defines standard evaluation rubrics and grading scales for human domain experts.
"""

from typing import Dict, List
from pydantic import BaseModel


class RubricCriterion(BaseModel):
    name: str
    description: str
    scale: Dict[int, str]


HUMAN_REVIEW_RUBRIC: Dict[str, RubricCriterion] = {
    "accuracy": RubricCriterion(
        name="Accuracy",
        description="Factual correctness and adherence to the expert interview statements.",
        scale={
            1: "Completely inaccurate or contains false information.",
            2: "Partially correct with significant factual mistakes.",
            3: "Mostly accurate with minor omissions.",
            4: "Fully accurate and faithful to the transcripts.",
        },
    ),
    "groundedness": RubricCriterion(
        name="Groundedness",
        description="Extent to which every substantive claim is backed by transcript evidence.",
        scale={
            1: "Ungrounded or entirely speculative.",
            2: "Substantial claims made without supporting citations.",
            3: "Most claims cited, minimal extrapolation.",
            4: "Strictly grounded in provided transcript evidence.",
        },
    ),
    "citation_quality": RubricCriterion(
        name="Citation Quality",
        description="Verifiability and accuracy of timestamped quotes and speaker attribution.",
        scale={
            1: "Fake or hallucinated quotes / incorrect expert attribution.",
            2: "Quotes modified or misattributed.",
            3: "Valid quotes with minor formatting differences.",
            4: "Exact verbatim quotes with accurate speaker & timestamp.",
        },
    ),
    "context_understanding": RubricCriterion(
        name="Context Understanding",
        description="Ability to capture market nuances, implicit meaning, and cross-market comparisons.",
        scale={
            1: "Misses core context or conflates different countries.",
            2: "Superficial understanding of market dynamics.",
            3: "Good synthesis of market specifics.",
            4: "Deep contextual synthesis across experts.",
        },
    ),
    "completeness": RubricCriterion(
        name="Completeness",
        description="Comprehensive answer addressing all facets of the user question.",
        scale={
            1: "Incomplete / fails to answer core question.",
            2: "Answers only a small part of the query.",
            3: "Addresses main points well.",
            4: "Exhaustive synthesis of all relevant transcript evidence.",
        },
    ),
    "hallucination": RubricCriterion(
        name="Hallucination Severity",
        description="Presence of invented statistics, ungrounded names, or non-existent claims.",
        scale={
            1: "Severe hallucination (invented experts/data).",
            2: "Moderate hallucination (unsupported figures/dates).",
            3: "Mild extrapolation beyond text.",
            4: "Zero hallucination / perfectly grounded.",
        },
    ),
}

REVIEWER_LABELS = [
    "Correct",
    "Partially Correct",
    "Incorrect",
    "Unsupported",
    "Hallucinated",
    "Missing Evidence",
    "Wrong Citation",
    "Wrong Quote",
    "Wrong Context",
]
