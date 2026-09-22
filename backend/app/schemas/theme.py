"""
ExpertLens AI — Theme Schemas

Pydantic models for cross-expert theme extraction.
"""

from pydantic import BaseModel


class ThemeEvidenceSchema(BaseModel):
    """Evidence supporting a theme from a specific expert."""
    chunk_id: str
    expert_name: str
    country: str
    quote: str
    timestamp: str

    model_config = {"from_attributes": True}


class ThemeSchema(BaseModel):
    """A theme identified across expert transcripts."""
    id: str
    theme_name: str
    description: str
    theme_type: str  # common_theme, different_emphasis
    evidence: list[ThemeEvidenceSchema] = []
    expert_count: int = 0

    model_config = {"from_attributes": True}


class ThemesResponse(BaseModel):
    """Full themes response."""
    themes: list[ThemeSchema] = []
    common_themes: int = 0
    different_emphasis: int = 0
