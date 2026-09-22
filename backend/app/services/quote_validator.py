"""
ExpertLens AI — Quote Validator

Verifies that quotes attributed to transcript sources actually exist
in the source text. This is a critical hallucination prevention mechanism.

Validation strategy:
1. Try exact substring match (after normalization)
2. Fall back to fuzzy matching with configurable threshold
3. If neither passes, the quote is marked as unverified and discarded
"""

import re
from difflib import SequenceMatcher

from app.config import settings


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison by:
    - lowercasing
    - collapsing whitespace
    - removing extra punctuation variation
    """
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    # Normalize common punctuation variants
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace("'", "'").replace("'", "'")
    text = text.replace('–', '-').replace('—', '-')
    return text


def validate_quote(quote: str, source_text: str, threshold: float | None = None) -> bool:
    """
    Validate that a quote exists in the source text.
    
    Args:
        quote: The quote to validate
        source_text: The original transcript text to check against
        threshold: Minimum similarity ratio (0.0-1.0). Defaults to config value.
        
    Returns:
        True if the quote is verified in the source text
    """
    if not quote or not source_text:
        return False

    if threshold is None:
        threshold = settings.QUOTE_SIMILARITY_THRESHOLD

    norm_quote = normalize_text(quote)
    norm_source = normalize_text(source_text)

    # Strategy 1: Exact substring match
    if norm_quote in norm_source:
        return True

    # Strategy 2: Sliding window fuzzy match
    # Check if any window of the source text matches the quote closely
    quote_words = norm_quote.split()
    source_words = norm_source.split()

    if len(quote_words) == 0:
        return False

    # Use a window slightly larger than the quote
    window_size = len(quote_words)
    best_ratio = 0.0

    for i in range(max(1, len(source_words) - window_size + 1)):
        window = ' '.join(source_words[i:i + window_size + 2])
        ratio = SequenceMatcher(None, norm_quote, window).ratio()
        best_ratio = max(best_ratio, ratio)
        
        if best_ratio >= threshold:
            return True

    return best_ratio >= threshold


def find_best_matching_quote(
    approximate_quote: str,
    source_text: str,
    threshold: float | None = None
) -> str | None:
    """
    Given an approximate quote, find the best matching segment in the source.
    
    This is used when the LLM produces a slightly paraphrased version
    and we want to replace it with the actual transcript text.
    
    Args:
        approximate_quote: The LLM-generated quote to match
        source_text: The original transcript text
        threshold: Minimum similarity ratio
        
    Returns:
        The best matching substring from the source, or None if no match
    """
    if threshold is None:
        threshold = settings.QUOTE_SIMILARITY_THRESHOLD

    norm_quote = normalize_text(approximate_quote)
    norm_source = normalize_text(source_text)

    quote_words = norm_quote.split()
    source_words = norm_source.split()

    if not quote_words or not source_words:
        return None

    window_size = len(quote_words)
    best_ratio = 0.0
    best_start = 0
    best_end = 0

    # Try different window sizes around the quote length
    for size_offset in range(-2, 4):
        current_window = max(3, window_size + size_offset)
        for i in range(max(1, len(source_words) - current_window + 1)):
            end = min(i + current_window, len(source_words))
            window = ' '.join(source_words[i:end])
            ratio = SequenceMatcher(None, norm_quote, window).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_start = i
                best_end = end

    if best_ratio >= threshold:
        # Return the original (non-normalized) text
        # Reconstruct from the original source
        original_words = source_text.split()
        if best_end <= len(original_words):
            return ' '.join(original_words[best_start:best_end])

    return None
