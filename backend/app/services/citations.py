"""
ExpertLens AI — Citations Service

Builds and formats citation objects linking answers to evidence chunks.
"""

from app.schemas.analysis import Source


def build_source(chunk: dict, quote: str = "") -> Source:
    """
    Build a Source citation from a chunk dict.
    
    Args:
        chunk: Enriched chunk dict from retrieval service
        quote: The verified quote text (defaults to chunk text)
        
    Returns:
        Source object with full citation metadata
    """
    return Source(
        chunk_id=chunk.get("chunk_id", chunk.get("id", "")),
        country=chunk.get("country", ""),
        expert_name=chunk.get("expert_name", ""),
        expert_role=chunk.get("expert_role", ""),
        timestamp=chunk.get("timestamp", ""),
        quote=quote or chunk.get("text", ""),
        verified=True,
    )
