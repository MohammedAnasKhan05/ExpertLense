"""
ExpertLens AI — Comparison Schemas

Pydantic models for cross-market comparison data.
"""

from pydantic import BaseModel
from app.schemas.analysis import Source


class ComparisonCell(BaseModel):
    """A single cell in the comparison table."""
    country: str
    expert_name: str
    expert_role: str
    summary: str
    sources: list[Source] = []


class ComparisonRow(BaseModel):
    """A row comparing all markets on one topic."""
    topic: str
    cells: list[ComparisonCell] = []


class ComparisonResponse(BaseModel):
    """Full comparison table response."""
    rows: list[ComparisonRow] = []
    countries: list[str] = ["France", "Germany", "United Kingdom"]
