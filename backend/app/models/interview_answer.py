"""
ExpertLens AI — Interview Answer Model

Stores generated answers for each interview question per expert.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class InterviewAnswer(Base):
    """A generated answer for a specific interview question and expert."""

    __tablename__ = "interview_answers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    question_id: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    expert_name: Mapped[str] = mapped_column(String(255), nullable=False)
    expert_role: Mapped[str] = mapped_column(String(255), nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[str] = mapped_column(String(20), default="high")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    evidence_items: Mapped[list["Evidence"]] = relationship(
        "Evidence", back_populates="answer", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<InterviewAnswer Q{self.question_id} {self.expert_name}>"
