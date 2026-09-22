"""
ExpertLens AI — Chat Schemas

Pydantic models for the Research AI chat interface.
"""

from pydantic import BaseModel
from app.schemas.analysis import Source


class ChatRequest(BaseModel):
    """A research question from the user."""
    question: str
    country_filter: str | None = None
    expert_filter: str | None = None


class ChatResponse(BaseModel):
    """A grounded answer with evidence citations."""
    answer: str
    sources: list[Source] = []
    confidence: str = "high"
    suggested_questions: list[str] = []
