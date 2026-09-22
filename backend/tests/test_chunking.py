"""
Unit tests for Transcript Chunking and Context Enrichment.
"""

from app.services.parser import ParsedTranscript, ParsedTurn
from app.services.chunking import chunk_transcript, create_context_text


def test_chunk_transcript():
    parsed = ParsedTranscript(
        expert_name="Dr. Test",
        expert_role="Surgeon",
        country="France",
        turns=[
            ParsedTurn(timestamp="00:00", speaker="Interviewer", text="Hello", index=0),
            ParsedTurn(timestamp="01:00", speaker="Dr. Test", text="We have 10 robots.", index=1),
        ],
    )
    chunks = chunk_transcript(parsed)
    assert len(chunks) == 2
    assert chunks[1].chunk_index == 1
    assert chunks[1].is_expert is True
    assert chunks[1].country == "France"


def test_create_context_text():
    parsed = ParsedTranscript(
        expert_name="Dr. Test",
        expert_role="Surgeon",
        country="France",
        turns=[
            ParsedTurn(timestamp="01:00", speaker="Dr. Test", text="We have 10 robots.", index=0),
        ],
    )
    chunks = chunk_transcript(parsed)
    context_text = create_context_text(chunks[0])
    assert "Dr. Test" in context_text
    assert "France" in context_text
    assert "[01:00]" in context_text
    assert "We have 10 robots." in context_text
