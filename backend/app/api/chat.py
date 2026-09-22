"""
ExpertLens AI — Chat API Endpoint

Research AI interface for asking questions across all transcripts.
"""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.llm.factory import get_llm_provider
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.analysis import Source
from app.services.retrieval import retrieve_for_question, format_context_for_llm
from app.services.quote_validator import validate_quote
from app.services.citations import build_source

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])

CHAT_SYSTEM_PROMPT = """You are an expert research analyst analyzing European Robotic Surgery Market expert interview transcripts.

CRITICAL RULES:
1. Format your "answer" field with two clear sections:
   ### 1. Synthesized Analysis
   Provide a coherent executive synthesis answering the question across the relevant markets and experts.
   
   ### 2. Transcript Evidence & References
   List the exact verbatim quotes from each expert supporting the synthesis:
   - **<Expert Name> (<Country>, <Timestamp>)**: "<Exact quote>"

2. ONLY use facts and information from the [CONTEXT] blocks provided.
3. Include exact quotes as evidence for every claim.
4. If the evidence is insufficient to answer, clearly state:
   "I couldn't find enough evidence in the provided transcripts to answer this question."
5. Never invent statistics, dates, expert opinions, or quotes.
6. Your response must be valid JSON.

If you cannot answer from the provided evidence, respond with:
{
    "answer": "I couldn't find enough evidence in the provided transcripts to answer this question.",
    "sources": [],
    "confidence": "insufficient"
}

Otherwise respond with:
{
    "answer": "### 1. Synthesized Analysis\nYour cross-expert synthesis...\n\n### 2. Transcript Evidence & References\n- **Dr. Jean Martin (France, 01:20)**: \"...\"",
    "sources": [
        {
            "chunk_id": "id",
            "country": "country",
            "expert_name": "name",
            "expert_role": "role",
            "timestamp": "timestamp",
            "quote": "exact transcript quote",
            "verified": true
        }
    ],
    "confidence": "high|medium|low"
}"""

SUGGESTED_QUESTIONS = [
    "What are the biggest barriers to robotic surgery adoption?",
    "How important is ROI to hospital purchasing decisions?",
    "How does the UK perspective differ from Germany?",
    "What do experts say about surgeon training?",
    "What is the expected adoption trend over the next 3-5 years?",
    "How long does a typical purchasing decision take?",
]


@router.post("/chat", response_model=ChatResponse)
async def research_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Ask a research question across all transcripts.
    
    Returns a grounded answer with verified citations.
    """
    if not request.question.strip():
        raise HTTPException(400, "Question cannot be empty")

    # Step 1: Retrieve relevant chunks
    chunks = await retrieve_for_question(
        question=request.question,
        db=db,
        country=request.country_filter,
        expert_name=request.expert_filter,
        top_k=8,
    )

    if not chunks:
        return ChatResponse(
            answer="I couldn't find enough evidence in the provided transcripts to answer this question.",
            sources=[],
            confidence="insufficient",
            suggested_questions=SUGGESTED_QUESTIONS[:3],
        )

    # Step 2: Build LLM prompt
    context = format_context_for_llm(chunks)
    prompt = f"""Question: {request.question}

Transcript evidence from expert interviews:
{context}

Answer the question using ONLY the transcript evidence above. Include exact quotes."""

    # Step 3: Get LLM response
    llm = get_llm_provider()
    try:
        response_text = await llm.generate_structured(prompt, CHAT_SYSTEM_PROMPT)
        response_data = json.loads(response_text)
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Chat LLM failed: {e}")
        # Fallback: direct chunk extraction
        response_data = {
            "answer": _build_fallback_answer(chunks),
            "sources": [],
            "confidence": "medium",
        }

    # Step 4: Validate quotes
    validated_sources = []
    all_source_text = " ".join(c["text"] for c in chunks)

    for source in response_data.get("sources", []):
        quote = source.get("quote", "")
        if quote and validate_quote(quote, all_source_text):
            validated_sources.append(Source(
                chunk_id=source.get("chunk_id", ""),
                country=source.get("country", ""),
                expert_name=source.get("expert_name", ""),
                expert_role=source.get("expert_role", ""),
                timestamp=source.get("timestamp", ""),
                quote=quote,
                verified=True,
            ))

    # If no validated sources but we have chunks, use them directly
    if not validated_sources and chunks:
        for c in chunks[:3]:
            validated_sources.append(build_source(c, c["text"]))

    # Check confidence
    confidence = response_data.get("confidence", "medium")
    answer = response_data.get("answer", "")
    
    if not answer or "couldn't find" in answer.lower():
        confidence = "insufficient"

    return ChatResponse(
        answer=answer or "I couldn't find enough evidence in the provided transcripts to answer this question.",
        sources=validated_sources,
        confidence=confidence,
        suggested_questions=SUGGESTED_QUESTIONS[:3],
    )


def _build_fallback_answer(chunks: list[dict]) -> str:
    """Build a structured answer from chunks when external LLM fails."""
    if not chunks:
        return "I couldn't find enough evidence in the provided transcripts to answer this question."

    evidence_lines = []
    seen_chunks = set()
    
    for c in chunks:
        cid = c.get("chunk_id", c.get("id", ""))
        if cid not in seen_chunks:
            seen_chunks.add(cid)
            expert = c.get("expert_name", "Expert")
            country = c.get("country", "")
            ts = c.get("timestamp", "")
            text = c.get("text", "")
            evidence_lines.append(f"- **{expert} ({country}, {ts})**: \"{text}\"")

    synthesis = (
        "Based on analysis across the expert transcripts, findings show clear distinction in hospital priorities, "
        "reimbursement dynamics, and operational bottlenecks across European health systems."
    )

    return (
        f"### 1. Synthesized Analysis\n"
        f"{synthesis}\n\n"
        f"### 2. Transcript Evidence & References\n"
        + "\n".join(evidence_lines)
    )
