"""
ExpertLens AI — Transcript Schemas

Pydantic request/response models for transcript operations.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class TranscriptChunkSchema(BaseModel):
    """A single transcript chunk with metadata."""
    id: str
    document_id: str
    timestamp: str
    speaker: str
    text: str
    chunk_index: int

    model_config = {"from_attributes": True}


class DocumentSchema(BaseModel):
    """A transcript document with metadata."""
    id: str
    filename: str
    expert_name: str
    expert_role: str
    country: str
    created_at: datetime
    chunk_count: int = 0

    model_config = {"from_attributes": True}


class DocumentDetailSchema(DocumentSchema):
    """Full transcript document with all chunks."""
    chunks: list[TranscriptChunkSchema] = []
    raw_text: str = ""


class TranscriptUploadResponse(BaseModel):
    """Response after uploading a transcript."""
    document_id: str
    expert_name: str
    country: str
    chunks_created: int
    message: str
