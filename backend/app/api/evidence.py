"""
ExpertLens AI — Evidence API Endpoint

Provides evidence detail views for the evidence drawer.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.retrieval import get_chunk_with_context
from app.schemas.evidence import EvidenceDetailSchema

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


@router.get("/{chunk_id}", response_model=EvidenceDetailSchema)
async def get_evidence_detail(
    chunk_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed evidence for the evidence drawer.
    
    Returns the chunk with surrounding context for full transparency.
    """
    result = await get_chunk_with_context(chunk_id, db)

    if not result:
        raise HTTPException(404, "Evidence chunk not found")

    return EvidenceDetailSchema(
        chunk_id=result["chunk_id"],
        expert_name=result["expert_name"],
        expert_role=result["expert_role"],
        country=result["country"],
        timestamp=result["timestamp"],
        quote=result["text"],
        context_before=result["context_before"],
        context_after=result["context_after"],
        full_text=result["full_text"],
        document_id=result["document_id"],
        verified=True,
    )
