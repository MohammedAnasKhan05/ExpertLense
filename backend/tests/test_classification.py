"""
Unit tests for Multi-Label Classification Dataset & Grader.
"""

import pytest
from evals.graders.classification_grader import ClassificationGrader, classify_chunk
from evals.datasets.classification_dataset import CLASSIFICATION_BENCHMARK, CLASSIFICATION_TAXONOMY


def test_taxonomy_labels_count():
    assert len(CLASSIFICATION_TAXONOMY) == 10
    assert "ADOPTION" in CLASSIFICATION_TAXONOMY
    assert "BARRIER" in CLASSIFICATION_TAXONOMY
    assert "ROI" in CLASSIFICATION_TAXONOMY
    assert "PURCHASING_TIMELINE" in CLASSIFICATION_TAXONOMY


def test_chunk_classification_heuristic():
    text = "The biggest barrier is still capital budget approval and economics."
    labels = classify_chunk(text)
    assert "BARRIER" in labels
    assert "ECONOMICS" in labels


def test_classification_benchmark_evaluation():
    res = ClassificationGrader.evaluate(CLASSIFICATION_BENCHMARK)
    assert res.total_samples == len(CLASSIFICATION_BENCHMARK)
    assert res.micro_f1 >= 0.70
    assert res.macro_f1 >= 0.70
    assert len(res.class_metrics) == 10
