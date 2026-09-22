"""
ExpertLens AI — Transcript API Endpoints

Handles transcript upload, listing, and detail views.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.document import Document
from app.models.transcript_chunk import TranscriptChunk
from app.services.ingestion import ingest_transcript, ingest_from_directory
from app.services.document_extractor import extract_text_from_file
from app.schemas.transcript import (
    DocumentSchema, DocumentDetailSchema, TranscriptUploadResponse, TranscriptChunkSchema
)
from app.config import settings

router = APIRouter(prefix="/api/transcripts", tags=["transcripts"])


class CreateTranscriptRequest(BaseModel):
    """Payload to create/ingest a new transcript directly."""
    expert_name: str = Field(..., description="Full name of expert (e.g. Dr. Maria Garcia)")
    expert_role: str = Field(..., description="Role/Title (e.g. Head of General Surgery)")
    country: str = Field(..., description="Market or Country (e.g. Spain, Italy, France, etc.)")
    raw_text: str = Field(..., description="Timestamped turns or transcript body text")
    filename: Optional[str] = None


@router.post("/create", response_model=TranscriptUploadResponse)
async def create_transcript(
    req: CreateTranscriptRequest,
    db: AsyncSession = Depends(get_db),
):
    """Add and ingest a new transcript from structured input text."""
    if not req.expert_name.strip():
        raise HTTPException(400, "Expert name is required")
    if not req.country.strip():
        raise HTTPException(400, "Country / Market is required")
    if not req.raw_text.strip():
        raise HTTPException(400, "Transcript text is required")

    filename = req.filename or f"Transcript_{req.country.replace(' ', '_')}_{req.expert_name.replace(' ', '_')}.txt"

    # Prepend standard header if not already formatted
    text = req.raw_text.strip()
    if not text.startswith("Expert"):
        formatted_text = (
            f"Expert – {req.expert_name}\n"
            f"Role: {req.expert_role}\n"
            f"Market: {req.country}\n\n"
            f"{text}"
        )
    else:
        formatted_text = text

    try:
        result = await ingest_transcript(formatted_text, filename, db)
    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        raise HTTPException(500, f"Ingestion failed: {str(e)}")

    return TranscriptUploadResponse(
        document_id=result["document_id"],
        expert_name=result["expert_name"],
        country=result["country"],
        chunks_created=result["chunks_created"],
        message=result["message"],
    )



@router.post("/upload", response_model=TranscriptUploadResponse)
async def upload_transcript(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload and ingest a transcript file (.txt, .pdf, .docx, .doc)."""
    if not file.filename:
        raise HTTPException(400, "Filename is missing")

    ext = os.path.splitext(file.filename)[1].lower()
    allowed_exts = {'.txt', '.pdf', '.docx', '.doc'}
    if ext not in allowed_exts:
        raise HTTPException(
            400,
            f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(allowed_exts))}"
        )

    content = await file.read()
    if not content:
        raise HTTPException(400, "Uploaded file is empty")

    try:
        text = extract_text_from_file(file.filename, content)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error extracting text from file: {str(e)}")

    if not text.strip():
        raise HTTPException(400, "No extractable text found in uploaded file")

    try:
        result = await ingest_transcript(text, file.filename, db)
    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        raise HTTPException(500, f"Ingestion failed: {str(e)}")

    return TranscriptUploadResponse(
        document_id=result["document_id"],
        expert_name=result["expert_name"],
        country=result["country"],
        chunks_created=result["chunks_created"],
        message=result["message"],
    )


@router.post("/seed")
async def seed_transcripts(db: AsyncSession = Depends(get_db)):
    """Seed the database with the demo transcripts from the data directory."""
    transcripts_dir = settings.TRANSCRIPTS_DIR
    if not os.path.exists(transcripts_dir):
        raise HTTPException(404, f"Transcripts directory not found: {transcripts_dir}")

    try:
        results = await ingest_from_directory(transcripts_dir, db)
    except Exception as e:
        raise HTTPException(500, f"Seeding failed: {str(e)}")

    return {"results": results, "total": len(results)}


@router.get("", response_model=list[DocumentSchema])
async def list_transcripts(db: AsyncSession = Depends(get_db)):
    """List all ingested transcripts."""
    result = await db.execute(
        select(Document).order_by(Document.country)
    )
    documents = result.scalars().all()

    response = []
    for doc in documents:
        # Get chunk count
        count_result = await db.execute(
            select(func.count(TranscriptChunk.id)).where(
                TranscriptChunk.document_id == doc.id
            )
        )
        chunk_count = count_result.scalar() or 0

        response.append(DocumentSchema(
            id=doc.id,
            filename=doc.filename,
            expert_name=doc.expert_name,
            expert_role=doc.expert_role,
            country=doc.country,
            created_at=doc.created_at,
            chunk_count=chunk_count,
        ))

    return response


@router.get("/{document_id}", response_model=DocumentDetailSchema)
async def get_transcript(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get full transcript detail with all chunks."""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(404, "Transcript not found")

    # Get chunks
    chunks_result = await db.execute(
        select(TranscriptChunk)
        .where(TranscriptChunk.document_id == document_id)
        .order_by(TranscriptChunk.chunk_index)
    )
    chunks = chunks_result.scalars().all()

    return DocumentDetailSchema(
        id=doc.id,
        filename=doc.filename,
        expert_name=doc.expert_name,
        expert_role=doc.expert_role,
        country=doc.country,
        created_at=doc.created_at,
        chunk_count=len(chunks),
        raw_text=doc.raw_text,
        chunks=[
            TranscriptChunkSchema(
                id=c.id,
                document_id=c.document_id,
                timestamp=c.timestamp,
                speaker=c.speaker,
                text=c.text,
                chunk_index=c.chunk_index,
            )
            for c in chunks
        ],
    )
