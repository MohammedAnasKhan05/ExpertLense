"""
ExpertLens AI — Analysis API Endpoints

Handles interview question analysis, comparison, and themes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.llm.factory import get_llm_provider
from app.schemas.analysis import AnalysisResponse, AnalyzeRequest
from app.schemas.comparison import ComparisonResponse
from app.schemas.theme import ThemesResponse
from app.services.analysis import analyze_all_questions, INTERVIEW_QUESTIONS
from app.services.comparison import get_comparison
from app.services.themes import extract_themes

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def run_analysis(
    request: AnalyzeRequest = AnalyzeRequest(),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger or retrieve interview question analysis.
    
    Analyzes all 6 interview questions for all ingested experts.
    Results are cached; use force_regenerate=true to rerun.
    """
    llm = get_llm_provider()
    try:
        result = await analyze_all_questions(db, llm, force=request.force_regenerate)
        return result
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")


@router.get("/questions", response_model=AnalysisResponse)
async def get_analysis(db: AsyncSession = Depends(get_db)):
    """Get existing analysis results (does not trigger new analysis)."""
    llm = get_llm_provider()
    try:
        result = await analyze_all_questions(db, llm, force=False)
        return result
    except Exception as e:
        raise HTTPException(500, f"Failed to load analysis: {str(e)}")


@router.get("/comparison", response_model=ComparisonResponse)
async def get_comparison_view(db: AsyncSession = Depends(get_db)):
    """Get the cross-market comparison table."""
    try:
        return await get_comparison(db)
    except Exception as e:
        raise HTTPException(500, f"Comparison failed: {str(e)}")


@router.get("/themes", response_model=ThemesResponse)
async def get_themes(
    force: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Get extracted themes across all experts."""
    llm = get_llm_provider()
    try:
        return await extract_themes(db, llm, force=force)
    except Exception as e:
        raise HTTPException(500, f"Theme extraction failed: {str(e)}")


@router.get("/questions/list")
async def list_interview_questions():
    """Return the six interview guide questions."""
    return {
        "questions": [
            {"id": i + 1, "text": q}
            for i, q in enumerate(INTERVIEW_QUESTIONS)
        ]
    }
