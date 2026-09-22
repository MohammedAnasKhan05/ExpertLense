"""
ExpertLens AI — Comparison Service

Builds the cross-market comparison matrix for all experts.
Neutral comparison — no ranking or scoring of countries.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview_answer import InterviewAnswer
from app.models.evidence import Evidence
from app.models.document import Document
from app.schemas.comparison import ComparisonCell, ComparisonRow, ComparisonResponse
from app.schemas.analysis import Source


COMPARISON_TOPICS = [
    ("Adoption Level", 1),
    ("Main Barriers", 2),
    ("Economics & ROI", 3),
    ("Training & Outcomes", 4),
    ("3–5 Year Outlook", 5),
    ("Purchase Timeline", 6),
]

COUNTRIES = ["France", "Germany", "United Kingdom"]


async def get_comparison(db: AsyncSession) -> ComparisonResponse:
    """
    Build the cross-market comparison table from existing analysis.
    
    Each row is a topic, each cell is a country's expert perspective
    with supporting evidence.
    
    Args:
        db: Database session
        
    Returns:
        ComparisonResponse with comparison matrix
    """
    rows = []

    for topic_name, question_id in COMPARISON_TOPICS:
        cells = []
        
        for country in COUNTRIES:
            # Get the answer for this question + country
            result = await db.execute(
                select(InterviewAnswer).where(
                    InterviewAnswer.question_id == question_id,
                    InterviewAnswer.country == country,
                )
            )
            answer = result.scalar_one_or_none()

            if answer:
                # Get evidence
                ev_result = await db.execute(
                    select(Evidence).where(Evidence.answer_id == answer.id)
                )
                evidence_items = ev_result.scalars().all()

                sources = [
                    Source(
                        chunk_id=ev.chunk_id,
                        country=country,
                        expert_name=answer.expert_name,
                        expert_role=answer.expert_role,
                        timestamp=ev.timestamp,
                        quote=ev.quote,
                        verified=ev.verified,
                    )
                    for ev in evidence_items
                ]

                cells.append(ComparisonCell(
                    country=country,
                    expert_name=answer.expert_name,
                    expert_role=answer.expert_role,
                    summary=answer.answer,
                    sources=sources,
                ))
            else:
                # No analysis available for this cell
                doc_result = await db.execute(
                    select(Document).where(Document.country == country)
                )
                doc = doc_result.scalar_one_or_none()
                cells.append(ComparisonCell(
                    country=country,
                    expert_name=doc.expert_name if doc else "",
                    expert_role=doc.expert_role if doc else "",
                    summary="Analysis not yet available.",
                    sources=[],
                ))

        rows.append(ComparisonRow(
            topic=topic_name,
            cells=cells,
        ))

    return ComparisonResponse(rows=rows, countries=COUNTRIES)
