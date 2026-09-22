"""
ExpertLens AI — Retrieval Service

Orchestrates semantic retrieval from ChromaDB and SQL database
to find relevant transcript evidence for questions.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transcript_chunk import TranscriptChunk
from app.models.document import Document
from app.vectorstore.chroma import query_chunks
from app.config import settings


async def retrieve_for_question(
    question: str,
    db: AsyncSession,
    country: str | None = None,
    expert_name: str | None = None,
    top_k: int | None = None,
) -> list[dict]:
    """
    Retrieve relevant transcript chunks for an interview question.
    
    Combines semantic search from ChromaDB with SQL metadata.
    
    Args:
        question: The question to find evidence for
        db: Database session
        country: Optional country filter
        expert_name: Optional expert filter
        top_k: Number of results to return
        
    Returns:
        List of enriched chunk dicts with full metadata
    """
    if top_k is None:
        top_k = settings.RETRIEVAL_TOP_K

    # Step 1: Semantic search in ChromaDB
    chroma_results = query_chunks(
        query_text=question,
        n_results=top_k,
        country_filter=country,
        expert_filter=expert_name,
        expert_only=True,
    )

    if not chroma_results:
        return []

    # Step 2: Enrich with SQL metadata
    chunk_ids = [r["id"] for r in chroma_results]
    
    stmt = (
        select(TranscriptChunk, Document)
        .join(Document, TranscriptChunk.document_id == Document.id)
        .where(TranscriptChunk.id.in_(chunk_ids))
    )
    result = await db.execute(stmt)
    rows = result.all()

    # Build a lookup
    chunk_lookup = {}
    for chunk, doc in rows:
        chunk_lookup[chunk.id] = {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "timestamp": chunk.timestamp,
            "speaker": chunk.speaker,
            "text": chunk.text,
            "chunk_index": chunk.chunk_index,
            "expert_name": doc.expert_name,
            "expert_role": doc.expert_role,
            "country": doc.country,
        }

    # Step 3: Merge ChromaDB scores with SQL metadata, preserving relevance order
    enriched = []
    for cr in chroma_results:
        chunk_id = cr["id"]
        if chunk_id in chunk_lookup:
            entry = chunk_lookup[chunk_id].copy()
            entry["distance"] = cr["distance"]
            entry["relevance_score"] = 1.0 - cr["distance"]  # cosine distance → similarity
            enriched.append(entry)

    return enriched


def format_context_for_llm(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a context string for the LLM prompt.
    
    Uses the [CONTEXT] block format that the local provider expects,
    and that provides clear structure for any LLM.
    
    Args:
        chunks: List of enriched chunk dicts from retrieve_for_question
        
    Returns:
        Formatted context string
    """
    if not chunks:
        return "No relevant transcript evidence found."

    parts = []
    for chunk in chunks:
        block = (
            f"[CONTEXT]\n"
            f"Expert: {chunk['expert_name']} | "
            f"Country: {chunk['country']} | "
            f"Role: {chunk['expert_role']} | "
            f"Timestamp: {chunk['timestamp']} | "
            f"ChunkID: {chunk['chunk_id']}\n"
            f"{chunk['text']}\n"
            f"[/CONTEXT]"
        )
        parts.append(block)

    return "\n\n".join(parts)


async def get_chunk_with_context(
    chunk_id: str,
    db: AsyncSession,
) -> dict | None:
    """
    Get a chunk with surrounding context for the evidence drawer.
    
    Returns the chunk plus its neighboring chunks for context.
    
    Args:
        chunk_id: The chunk ID to look up
        db: Database session
        
    Returns:
        Dict with chunk data plus context_before and context_after
    """
    # Get the target chunk
    stmt = (
        select(TranscriptChunk, Document)
        .join(Document, TranscriptChunk.document_id == Document.id)
        .where(TranscriptChunk.id == chunk_id)
    )
    result = await db.execute(stmt)
    row = result.first()

    if not row:
        return None

    chunk, doc = row

    # Get surrounding chunks
    stmt_context = (
        select(TranscriptChunk)
        .where(TranscriptChunk.document_id == chunk.document_id)
        .where(TranscriptChunk.chunk_index.between(
            max(0, chunk.chunk_index - 2),
            chunk.chunk_index + 2
        ))
        .order_by(TranscriptChunk.chunk_index)
    )
    context_result = await db.execute(stmt_context)
    context_chunks = context_result.scalars().all()

    context_before = ""
    context_after = ""
    for cc in context_chunks:
        if cc.chunk_index < chunk.chunk_index:
            context_before += f"[{cc.timestamp}] {cc.speaker}: {cc.text}\n"
        elif cc.chunk_index > chunk.chunk_index:
            context_after += f"[{cc.timestamp}] {cc.speaker}: {cc.text}\n"

    return {
        "chunk_id": chunk.id,
        "document_id": chunk.document_id,
        "expert_name": doc.expert_name,
        "expert_role": doc.expert_role,
        "country": doc.country,
        "timestamp": chunk.timestamp,
        "speaker": chunk.speaker,
        "text": chunk.text,
        "context_before": context_before.strip(),
        "context_after": context_after.strip(),
        "full_text": doc.raw_text,
    }
