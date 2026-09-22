"""
ExpertLens AI — Transcript Chunking

Creates timestamp-aware chunks from parsed transcripts.
Each chunk preserves full metadata for evidence tracing.
Chunks are aligned to speaker turns, not arbitrary text splits.
"""

from dataclasses import dataclass
from app.services.parser import ParsedTranscript, ParsedTurn


@dataclass
class Chunk:
    """A metadata-rich transcript chunk ready for embedding and storage."""
    text: str
    timestamp: str
    speaker: str
    expert_name: str
    expert_role: str
    country: str
    chunk_index: int
    is_expert: bool


def chunk_transcript(parsed: ParsedTranscript) -> list[Chunk]:
    """
    Convert a parsed transcript into chunks aligned to speaker turns.
    
    Each speaker turn becomes one chunk, preserving:
    - timestamp
    - speaker identity
    - expert metadata
    - chunk ordering
    
    For short transcripts (< 50 turns), each turn = 1 chunk.
    For longer transcripts, adjacent turns can be merged while
    preserving timestamp boundaries.
    
    Args:
        parsed: A ParsedTranscript from the parser
        
    Returns:
        List of Chunk objects ready for storage and embedding
    """
    chunks: list[Chunk] = []

    for i, turn in enumerate(parsed.turns):
        is_expert = "interviewer" not in turn.speaker.lower()
        
        chunks.append(Chunk(
            text=turn.text,
            timestamp=turn.timestamp,
            speaker=turn.speaker,
            expert_name=parsed.expert_name,
            expert_role=parsed.expert_role,
            country=parsed.country,
            chunk_index=i,
            is_expert=is_expert,
        ))

    return chunks


def create_context_text(chunk: Chunk) -> str:
    """
    Create enriched text for embedding that includes metadata context.
    This helps the embedding model understand who said what and when.
    
    Args:
        chunk: A Chunk object
        
    Returns:
        Context-enriched text string for embedding
    """
    parts = [
        f"[{chunk.country}] [{chunk.expert_name}] [{chunk.timestamp}]",
        f"{chunk.speaker}: {chunk.text}"
    ]
    return " ".join(parts)
