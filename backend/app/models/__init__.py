"""
ExpertLens AI — Database Models Package

Imports all SQLAlchemy ORM models so they are registered
with Base.metadata and relationship mappers can resolve each other.
"""

from app.models.document import Document
from app.models.transcript_chunk import TranscriptChunk
from app.models.interview_answer import InterviewAnswer
from app.models.evidence import Evidence
from app.models.theme import Theme, ThemeEvidence

__all__ = [
    "Document",
    "TranscriptChunk",
    "InterviewAnswer",
    "Evidence",
    "Theme",
    "ThemeEvidence",
]
