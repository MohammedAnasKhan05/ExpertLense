"""
ExpertLens AI — Multi-Label Classification Grader

Evaluates multi-label topic classification of transcript chunks against
the 10-class taxonomy:
ADOPTION, BARRIER, ECONOMICS, ROI, TRAINING, CLINICAL_OUTCOME,
OUTLOOK, PURCHASING_TIMELINE, UTILIZATION, FUNDING.

Calculates:
- Per-class Precision, Recall, F1
- Global Micro F1
- Global Macro F1
"""

from typing import Dict, List, Set
from pydantic import BaseModel

from evals.datasets.classification_dataset import CLASSIFICATION_BENCHMARK, CLASSIFICATION_TAXONOMY, LabeledChunk


class ClassMetric(BaseModel):
    """Per-category classification metrics."""
    label: str
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0


class ClassificationResult(BaseModel):
    """Overall multi-label classification evaluation metrics."""
    total_samples: int = 0
    micro_precision: float = 0.0
    micro_recall: float = 0.0
    micro_f1: float = 0.0
    macro_precision: float = 0.0
    macro_recall: float = 0.0
    macro_f1: float = 0.0
    class_metrics: Dict[str, ClassMetric] = {}


# Heuristic rule-based chunk classifier for local deterministic classification
KEYWORDS_MAP: Dict[str, List[str]] = {
    "ADOPTION": ["adoption", "growing", "concentrated", "standard", "increase", "uneven"],
    "BARRIER": ["barrier", "holding adoption back", "issue", "cost is the first barrier", "stalls"],
    "ECONOMICS": ["economic", "finance", "capital", "cost", "budget", "total cost of ownership"],
    "ROI": ["roi", "pay for itself", "return", "business case"],
    "TRAINING": ["training", "trained", "surgeons", "theatre staff", "comfortable using"],
    "CLINICAL_OUTCOME": ["clinical outcome", "clinical argument", "length of stay", "patient outcomes"],
    "OUTLOOK": ["next three to five years", "3-5 years", "outlook", "accelerate", "expect", "growth"],
    "PURCHASING_TIMELINE": ["timeline", "decision-making", "months", "six to twelve", "nine to eighteen", "six to nine", "cycle"],
    "UTILIZATION": ["utilisation", "utilization", "volume", "used enough", "procedure volume"],
    "FUNDING": ["funding", "budget", "capital budget", "capital cycle", "tariffs"],
}


def classify_chunk(text: str) -> List[str]:
    """Classifies a chunk into multi-label categories based on semantic keyword density."""
    lower_t = text.lower()
    predicted = []
    for label, keywords in KEYWORDS_MAP.items():
        if any(kw in lower_t for kw in keywords):
            predicted.append(label)
    return predicted or ["ECONOMICS"]


class ClassificationGrader:
    """Evaluates classification performance across the transcript dataset."""

    @staticmethod
    def evaluate(samples: List[LabeledChunk] = CLASSIFICATION_BENCHMARK) -> ClassificationResult:
        metrics: Dict[str, ClassMetric] = {
            label: ClassMetric(label=label) for label in CLASSIFICATION_TAXONOMY
        }

        total_tp = 0
        total_fp = 0
        total_fn = 0

        for item in samples:
            true_set = set(item.labels)
            pred_set = set(classify_chunk(item.text))

            for label in CLASSIFICATION_TAXONOMY:
                is_true = label in true_set
                is_pred = label in pred_set

                if is_true and is_pred:
                    metrics[label].true_positives += 1
                    total_tp += 1
                elif not is_true and is_pred:
                    metrics[label].false_positives += 1
                    total_fp += 1
                elif is_true and not is_pred:
                    metrics[label].false_negatives += 1
                    total_fn += 1

        # Calculate per-class metrics
        macro_prec_sum = 0.0
        macro_rec_sum = 0.0
        macro_f1_sum = 0.0

        for label, m in metrics.items():
            denom_p = m.true_positives + m.false_positives
            m.precision = round(m.true_positives / denom_p, 3) if denom_p > 0 else 0.0

            denom_r = m.true_positives + m.false_negatives
            m.recall = round(m.true_positives / denom_r, 3) if denom_r > 0 else 0.0

            denom_f = m.precision + m.recall
            m.f1 = round((2 * m.precision * m.recall) / denom_f, 3) if denom_f > 0 else 0.0

            macro_prec_sum += m.precision
            macro_rec_sum += m.recall
            macro_f1_sum += m.f1

        n_classes = len(CLASSIFICATION_TAXONOMY)
        macro_prec = round(macro_prec_sum / n_classes, 3)
        macro_rec = round(macro_rec_sum / n_classes, 3)
        macro_f1 = round(macro_f1_sum / n_classes, 3)

        # Micro metrics
        micro_p = round(total_tp / (total_tp + total_fp), 3) if (total_tp + total_fp) > 0 else 0.0
        micro_r = round(total_tp / (total_tp + total_fn), 3) if (total_tp + total_fn) > 0 else 0.0
        micro_f1 = round((2 * micro_p * micro_r) / (micro_p + micro_r), 3) if (micro_p + micro_r) > 0 else 0.0

        return ClassificationResult(
            total_samples=len(samples),
            micro_precision=micro_p,
            micro_recall=micro_r,
            micro_f1=micro_f1,
            macro_precision=macro_prec,
            macro_recall=macro_rec,
            macro_f1=macro_f1,
            class_metrics=metrics,
        )
