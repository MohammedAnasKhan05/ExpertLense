"""
ExpertLens AI — Evidence Schemas

Pydantic models for evidence inspection.
"""

from pydantic import BaseModel


class EvidenceDetailSchema(BaseModel):
    """Detailed evidence view for the evidence drawer."""
    chunk_id: str
    expert_name: str
    expert_role: str
    country: str
    timestamp: str
    quote: str
    context_before: str = ""
    context_after: str = ""
    full_text: str = ""
    document_id: str = ""
    verified: bool = True
