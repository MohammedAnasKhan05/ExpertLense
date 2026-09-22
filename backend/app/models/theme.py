"""
ExpertLens AI — Theme Model

Represents cross-expert themes extracted from transcript analysis.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Theme(Base):
    """A recurring theme identified across expert transcripts."""

    __tablename__ = "themes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    theme_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    theme_type: Mapped[str] = mapped_column(
        String(50), default="common_theme"
    )  # common_theme, different_emphasis
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    evidence_items: Mapped[list["ThemeEvidence"]] = relationship(
        "ThemeEvidence", back_populates="theme", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Theme {self.theme_name} ({self.theme_type})>"


class ThemeEvidence(Base):
    """Links a theme to supporting evidence from specific experts."""

    __tablename__ = "theme_evidence"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    theme_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("themes.id"), nullable=False
    )
    chunk_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transcript_chunks.id"), nullable=False
    )
    expert_name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    quote: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[str] = mapped_column(String(10), nullable=False)

    # Relationships
    theme: Mapped["Theme"] = relationship("Theme", back_populates="evidence_items")

    def __repr__(self) -> str:
        return f"<ThemeEvidence {self.expert_name} -> {self.theme_id}>"
