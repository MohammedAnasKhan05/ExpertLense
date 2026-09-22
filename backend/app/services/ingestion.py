"""
ExpertLens AI — Ingestion Service

Orchestrates the full ingestion pipeline:
File → Parse → Chunk → SQL → Embed → ChromaDB

Handles both file uploads and seed data loading.
"""

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.transcript_chunk import TranscriptChunk
from app.services.parser import parse_transcript
from app.services.chunking import chunk_transcript
from app.vectorstore.chroma import add_chunks


async def ingest_transcript(
    text: str,
    filename: str,
    db: AsyncSession,
) -> dict:
    """
    Ingest a single transcript through the full pipeline.
    
    Args:
        text: Raw transcript text content
        filename: Original filename
        db: Database session
        
    Returns:
        Dict with document_id, expert_name, country, chunks_created
    """
    # Step 1: Parse the transcript
    parsed = parse_transcript(text, filename)

    if not parsed.expert_name:
        raise ValueError(f"Could not extract expert name from {filename}")
    if not parsed.turns:
        raise ValueError(f"No speaker turns found in {filename}")

    # Step 2: Check for duplicate (idempotent ingestion)
    existing = await db.execute(
        select(Document).where(
            Document.expert_name == parsed.expert_name,
            Document.country == parsed.country,
        )
    )
    existing_doc = existing.scalar_one_or_none()
    if existing_doc:
        return {
            "document_id": existing_doc.id,
            "expert_name": existing_doc.expert_name,
            "country": existing_doc.country,
            "chunks_created": 0,
            "message": "Already ingested",
        }

    # Step 3: Create document record
    doc = Document(
        filename=filename,
        expert_name=parsed.expert_name,
        expert_role=parsed.expert_role,
        country=parsed.country,
        raw_text=text,
    )
    db.add(doc)
    await db.flush()

    # Step 4: Create chunks
    chunks = chunk_transcript(parsed)
    chunk_ids = []
    
    for chunk in chunks:
        tc = TranscriptChunk(
            document_id=doc.id,
            timestamp=chunk.timestamp,
            speaker=chunk.speaker,
            text=chunk.text,
            chunk_index=chunk.chunk_index,
        )
        db.add(tc)
        await db.flush()
        chunk_ids.append(tc.id)

    await db.commit()

    # Step 5: Index in ChromaDB
    indexed = add_chunks(chunks, chunk_ids)

    return {
        "document_id": doc.id,
        "expert_name": parsed.expert_name,
        "country": parsed.country,
        "chunks_created": indexed,
        "message": f"Successfully ingested {filename}",
    }


async def ingest_from_directory(
    directory: str,
    db: AsyncSession,
) -> list[dict]:
    """
    Ingest all transcript files from a directory.
    
    Args:
        directory: Path to directory containing transcript files
        db: Database session
        
    Returns:
        List of ingestion results per file
    """
    results = []
    dir_path = Path(directory)

    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    for filepath in sorted(dir_path.glob("Transcript_*.txt")):
        text = filepath.read_text(encoding="utf-8")
        try:
            result = await ingest_transcript(text, filepath.name, db)
            results.append(result)
        except Exception as e:
            results.append({
                "filename": filepath.name,
                "error": str(e),
                "message": f"Failed to ingest {filepath.name}",
            })

    return results
