"""
ExpertLens AI — Evidence Model

Links an answer to its supporting transcript chunk and verified quote.
This is the core citation model that ensures every insight is traceable.
"""

import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Evidence(Base):
    """A verified piece of evidence linking an answer to a transcript chunk."""

    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    answer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("interview_answers.id"), nullable=True
    )
    chunk_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transcript_chunks.id"), nullable=False
    )
    quote: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[str] = mapped_column(String(10), nullable=False)
    verified: Mapped[bool] = mapped_column(default=True)

    # Relationships
    answer: Mapped["InterviewAnswer"] = relationship(
        "InterviewAnswer", back_populates="evidence_items"
    )
    chunk: Mapped["TranscriptChunk"] = relationship(
        "TranscriptChunk", back_populates="evidence_items"
    )

    def __repr__(self) -> str:
        return f"<Evidence [{self.timestamp}] verified={self.verified}>"
