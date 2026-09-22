"""
ExpertLens AI — Transcript Chunk Model

Represents a single timestamped speaker turn within a transcript.
Each chunk preserves its original metadata for evidence tracing.
"""

import uuid
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TranscriptChunk(Base):
    """A single timestamped speaker turn within a transcript."""

    __tablename__ = "transcript_chunks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("documents.id"), nullable=False
    )
    timestamp: Mapped[str] = mapped_column(String(10), nullable=False)
    speaker: Mapped[str] = mapped_column(String(255), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
    evidence_items: Mapped[list["Evidence"]] = relationship(
        "Evidence", back_populates="chunk", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<TranscriptChunk [{self.timestamp}] {self.speaker}>"
