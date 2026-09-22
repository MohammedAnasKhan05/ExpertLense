"""
ExpertLens AI — Regression Suite & Release Gates

Evaluates the benchmark dataset and enforces configurable release gates from .env:
- EVAL_MIN_ACCURACY (default: 0.85)
- EVAL_MIN_GROUNDEDNESS (default: 0.90)
- EVAL_MAX_HALLUCINATION (default: 0.05)
- EVAL_MIN_CITATION_COVERAGE (default: 0.85)

Exits with:
  Code 0: All release gates PASS
  Code 1: One or more release gates FAILED (blocks deployment)

Usage:
    cd backend
    python -m evals.regression
"""

import asyncio
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from evals.runner import run_evaluation
from evals.report import EvaluationReporter


def check_release_gates(report) -> bool:
    """Checks report metrics against configured release gate thresholds."""
    # Configurable thresholds from environment variables
    min_accuracy = float(os.getenv("EVAL_MIN_ACCURACY", "0.85"))
    min_groundedness = float(os.getenv("EVAL_MIN_GROUNDEDNESS", "0.90"))
    max_hallucination = float(os.getenv("EVAL_MAX_HALLUCINATION", "0.05"))
    min_citation_coverage = float(os.getenv("EVAL_MIN_CITATION_COVERAGE", "0.85"))

    w = 80
    print("\n" + "=" * w)
    print("  EXPERTLENS AI — RELEASE GATE REGRESSION VERIFICATION".center(w))
    print("=" * w)
    print(f" {'GATE CRITERION':<30} | {'REQUIRED':<12} | {'ACTUAL':<12} | {'STATUS':<15}")
    print("-" * w)

    all_passed = True

    # Gate 1: Accuracy
    acc_pass = report.mean_accuracy >= min_accuracy
    all_passed = all_passed and acc_pass
    print(f" {'Minimum Accuracy':<30} | {f'>= {min_accuracy:.2f}':<12} | {f'{report.mean_accuracy:.2f}':<12} | {'[PASS]' if acc_pass else '[FAIL REGRESSION]'}")

    # Gate 2: Groundedness
    grd_pass = report.mean_groundedness >= min_groundedness
    all_passed = all_passed and grd_pass
    print(f" {'Minimum Groundedness':<30} | {f'>= {min_groundedness:.2f}':<12} | {f'{report.mean_groundedness:.2f}':<12} | {'[PASS]' if grd_pass else '[FAIL REGRESSION]'}")

    # Gate 3: Hallucination Rate
    hal_pass = report.mean_hallucination_rate <= max_hallucination
    all_passed = all_passed and hal_pass
    print(f" {'Max Hallucination Rate':<30} | {f'<= {max_hallucination:.2f}':<12} | {f'{report.mean_hallucination_rate:.2f}':<12} | {'[PASS]' if hal_pass else '[FAIL REGRESSION]'}")

    # Gate 4: Citation Coverage
    cit_pass = report.mean_citation_coverage >= min_citation_coverage
    all_passed = all_passed and cit_pass
    print(f" {'Min Citation Coverage':<30} | {f'>= {min_citation_coverage:.2f}':<12} | {f'{report.mean_citation_coverage:.2f}':<12} | {'[PASS]' if cit_pass else '[FAIL REGRESSION]'}")

    print("=" * w)

    if all_passed:
        print("\n  >>> RELEASE GATES PASSED: Build is approved for deployment. <<<\n")
    else:
        print("\n  >>> RELEASE GATES FAILED: Regressions detected! Deployment blocked. <<<\n")

    return all_passed


def main():
    print("[1/2] Running evaluation pipeline across benchmark cases...")
    report = asyncio.run(run_evaluation())
    EvaluationReporter.print_terminal_summary(report)

    print("[2/2] Checking release gates...")
    passed = check_release_gates(report)

    if not passed:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
