"""
ExpertLens AI — Analysis Schemas

Pydantic models for structured AI output including grounded answers and sources.
These enforce that every LLM response carries citation metadata.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class Source(BaseModel):
    """A verified source citation from a transcript."""
    chunk_id: str
    country: str
    expert_name: str
    expert_role: str
    timestamp: str
    quote: str
    verified: bool = True


class GroundedAnswer(BaseModel):
    """An answer grounded in transcript evidence."""
    answer: str
    sources: list[Source] = []
    confidence: str = "high"  # high, medium, low, insufficient


class QuestionAnalysis(BaseModel):
    """Analysis of a single interview question across one expert."""
    question_id: int
    question_text: str
    expert_name: str
    expert_role: str
    country: str
    answer: str
    sources: list[Source] = []
    confidence: str = "high"


class QuestionAnalysisGroup(BaseModel):
    """All expert answers for a single interview question."""
    question_id: int
    question_text: str
    analyses: list[QuestionAnalysis] = []


class AnalysisResponse(BaseModel):
    """Full analysis response covering all questions."""
    questions: list[QuestionAnalysisGroup] = []
    total_questions: int = 6
    total_experts: int = 3
    total_evidence: int = 0


class AnalyzeRequest(BaseModel):
    """Request to trigger analysis."""
    force_regenerate: bool = False
