"""
Unit tests for the Quote Validator service.
"""

from app.services.quote_validator import validate_quote, normalize_text, find_best_matching_quote


def test_normalize_text():
    raw = "  This   is a \"TEST\"   with — dashes  "
    norm = normalize_text(raw)
    assert "test" in norm
    assert "  " not in norm


def test_exact_quote_validation():
    source = "Robotics has definitely moved from an exploratory technology to an expected standard of care."
    quote = "exploratory technology to an expected standard of care"
    assert validate_quote(quote, source) is True


def test_normalized_quote_validation():
    source = "Robotics has definitely moved from an exploratory technology."
    quote = "Robotics has definitely moved from an exploratory technology."
    assert validate_quote(quote, source) is True


def test_fuzzy_quote_validation():
    source = "The capital expenditure for a Da Vinci system is around 1.5 to 2 million euros."
    quote = "capital expenditure for Da Vinci system is around 1.5 to 2 million euros"
    assert validate_quote(quote, source, threshold=0.7) is True


def test_hallucinated_quote_rejected():
    source = "Robotics has definitely moved from an exploratory technology."
    quote = "Our hospital completely banned all robotic systems due to catastrophic failure."
    assert validate_quote(quote, source) is False


def test_empty_quote_handling():
    assert validate_quote("", "some text") is False
    assert validate_quote("some quote", "") is False


def test_find_best_matching_quote():
    source = "Full text here: We saw a 30% reduction in length of stay. That was huge."
    quote = "saw a 30% reduction in length of stay"
    matched = find_best_matching_quote(quote, source)
    assert matched is not None
    assert "30% reduction" in matched
