"""
ExpertLens AI — Quote & Citation Verifier Grader

Deterministic verification of generated quotes against raw source transcripts:
Generated quote → normalize → search original transcript → PASS/FAIL
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from app.services.quote_validator import normalize_text, validate_quote, find_best_matching_quote
from app.config import settings


class QuoteValidationResult(BaseModel):
    """Result of quote verification for an answer's citations."""
    test_id: str
    total_quotes: int = 0
    verified_quotes: int = 0
    failed_quotes: int = 0
    pass_rate: float = 1.0
    quote_details: List[Dict[str, Any]] = []
    passed: bool = True


class QuoteGrader:
    """Verifies quotes and timestamps deterministically."""

    @staticmethod
    def verify_quotes(test_id: str, citations: List[Dict[str, Any]], raw_corpus_text: str = "") -> QuoteValidationResult:
        res = QuoteValidationResult(test_id=test_id, total_quotes=len(citations))

        if not citations:
            return res

        # If raw_corpus_text is not provided, load all 3 transcripts
        if not raw_corpus_text:
            transcripts_dir = Path(settings.TRANSCRIPTS_DIR)
            texts = []
            if transcripts_dir.exists():
                for f in transcripts_dir.glob("*.txt"):
                    if "Interview_Guide" not in f.name:
                        try:
                            texts.append(f.read_text(encoding="utf-8"))
                        except Exception:
                            pass
            raw_corpus_text = " ".join(texts)

        for cite in citations:
            quote = cite.get("quote", "").strip()
            expert = cite.get("expert_name", "")
            timestamp = cite.get("timestamp", "")

            if not quote:
                res.failed_quotes += 1
                res.quote_details.append({
                    "quote": "",
                    "status": "FAIL",
                    "reason": "Empty quote",
                })
                continue

            # Deterministic check
            is_valid = validate_quote(quote, raw_corpus_text)
            matched_segment = quote if is_valid else find_best_matching_quote(quote, raw_corpus_text)

            if is_valid or matched_segment:
                res.verified_quotes += 1
                res.quote_details.append({
                    "quote": quote,
                    "matched_segment": matched_segment or quote,
                    "status": "PASS",
                    "expert": expert,
                    "timestamp": timestamp,
                })
            else:
                res.failed_quotes += 1
                res.quote_details.append({
                    "quote": quote,
                    "status": "FAIL",
                    "reason": "Quote not found in original transcript corpus",
                    "expert": expert,
                    "timestamp": timestamp,
                })

        res.pass_rate = round(res.verified_quotes / max(1, res.total_quotes), 3)
        res.passed = res.failed_quotes == 0

        return res
