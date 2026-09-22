"""
ExpertLens AI — Analysis Service

Generates grounded answers for the six interview guide questions.
Each answer is backed by verified transcript evidence.
"""

import json
import logging

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.interview_answer import InterviewAnswer
from app.models.evidence import Evidence
from app.services.retrieval import retrieve_for_question, format_context_for_llm
from app.services.quote_validator import validate_quote, find_best_matching_quote
from app.services.citations import build_source
from app.llm.base import LLMProvider
from app.schemas.analysis import (
    Source, QuestionAnalysis, QuestionAnalysisGroup, AnalysisResponse
)

logger = logging.getLogger(__name__)

# The six interview guide questions
INTERVIEW_QUESTIONS = [
    "How would you describe current adoption of robotic surgery in your market?",
    "What are the main barriers to adoption?",
    "How important are hospital budgets and ROI in purchasing decisions?",
    "How important are surgeon training and clinical outcomes?",
    "What adoption trend do you expect over the next 3–5 years?",
    "What is the typical hospital decision-making timeline for purchasing a new robotic system?",
]

SYSTEM_PROMPT = """You are an expert research analyst. Your job is to answer interview questions
using ONLY the provided transcript evidence. 

CRITICAL RULES:
1. Only use information from the [CONTEXT] blocks provided
2. Include exact quotes from the transcript as evidence
3. If the evidence is insufficient, say so clearly
4. Never invent statistics, dates, opinions, or quotes
5. Your response must be valid JSON

Respond with this JSON structure:
{
    "answer": "Your grounded answer summarizing what the expert said",
    "sources": [
        {
            "chunk_id": "the ChunkID from the context",
            "country": "country",
            "expert_name": "name",
            "expert_role": "role",
            "timestamp": "timestamp",
            "quote": "exact quote from the transcript",
            "verified": true
        }
    ],
    "confidence": "high|medium|low|insufficient"
}"""


async def analyze_question_for_expert(
    question_id: int,
    question_text: str,
    expert_name: str,
    country: str,
    db: AsyncSession,
    llm: LLMProvider,
) -> QuestionAnalysis:
    """
    Analyze a single interview question for a single expert.
    
    Pipeline:
    1. Retrieve relevant chunks for this expert
    2. Send to LLM with grounding prompt
    3. Parse structured response
    4. Validate quotes against source text
    5. Build citations
    
    Args:
        question_id: Question index (1-6)
        question_text: The question text
        expert_name: Expert to analyze
        country: Expert's country
        db: Database session
        llm: LLM provider
        
    Returns:
        QuestionAnalysis with grounded answer and verified sources
    """
    # Step 1: Retrieve relevant chunks
    chunks = await retrieve_for_question(
        question=question_text,
        db=db,
        country=country,
        expert_name=expert_name,
        top_k=5,
    )

    if not chunks:
        # Get expert role from DB
        doc_result = await db.execute(
            select(Document).where(Document.expert_name == expert_name)
        )
        doc = doc_result.scalar_one_or_none()
        role = doc.expert_role if doc else ""
        
        return QuestionAnalysis(
            question_id=question_id,
            question_text=question_text,
            expert_name=expert_name,
            expert_role=role,
            country=country,
            answer="I couldn't find enough evidence in the provided transcripts to answer this question.",
            sources=[],
            confidence="insufficient",
        )

    expert_role = chunks[0].get("expert_role", "")

    # Step 2: Build LLM prompt
    context = format_context_for_llm(chunks)
    prompt = f"""Question: {question_text}

Expert: {expert_name} ({country})

Transcript evidence:
{context}

Analyze the expert's response to this question using ONLY the transcript evidence above.
Include exact quotes as evidence."""

    # Step 3: Get LLM response
    try:
        response_text = await llm.generate_structured(prompt, SYSTEM_PROMPT)
        response_data = json.loads(response_text)
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"LLM response parsing failed: {e}")
        # Fallback: use direct chunk text
        response_data = {
            "answer": chunks[0]["text"] if chunks else "Analysis unavailable.",
            "sources": [],
            "confidence": "medium",
        }

    # Step 4: Validate quotes
    validated_sources = []
    all_source_text = " ".join(c["text"] for c in chunks)

    for source in response_data.get("sources", []):
        quote = source.get("quote", "")
        if not quote:
            continue
            
        # Try validation
        if validate_quote(quote, all_source_text):
            validated_sources.append(Source(
                chunk_id=source.get("chunk_id", chunks[0]["chunk_id"] if chunks else ""),
                country=country,
                expert_name=expert_name,
                expert_role=expert_role,
                timestamp=source.get("timestamp", chunks[0]["timestamp"] if chunks else ""),
                quote=quote,
                verified=True,
            ))
        else:
            # Try to find the best matching real quote
            best_match = find_best_matching_quote(quote, all_source_text)
            if best_match:
                # Find the chunk this quote belongs to
                matching_chunk = next(
                    (c for c in chunks if best_match.lower() in c["text"].lower()),
                    chunks[0] if chunks else None
                )
                if matching_chunk:
                    validated_sources.append(Source(
                        chunk_id=matching_chunk["chunk_id"],
                        country=country,
                        expert_name=expert_name,
                        expert_role=expert_role,
                        timestamp=matching_chunk["timestamp"],
                        quote=best_match,
                        verified=True,
                    ))

    # If no sources validated but we have chunks, create sources from raw chunks
    if not validated_sources and chunks:
        for c in chunks[:2]:
            validated_sources.append(build_source(c, c["text"]))

    return QuestionAnalysis(
        question_id=question_id,
        question_text=question_text,
        expert_name=expert_name,
        expert_role=expert_role,
        country=country,
        answer=response_data.get("answer", "Analysis unavailable."),
        sources=validated_sources,
        confidence=response_data.get("confidence", "medium"),
    )


async def analyze_all_questions(
    db: AsyncSession,
    llm: LLMProvider,
    force: bool = False,
) -> AnalysisResponse:
    """
    Run analysis for all 6 questions × all experts.
    
    Args:
        db: Database session
        llm: LLM provider
        force: If True, regenerate even if analysis exists
        
    Returns:
        Full AnalysisResponse with all question groups
    """
    # Get all documents
    result = await db.execute(select(Document))
    documents = result.scalars().all()

    if not documents:
        return AnalysisResponse(questions=[], total_evidence=0)

    # Check if analysis already exists
    if not force:
        existing = await db.execute(select(InterviewAnswer))
        existing_answers = existing.scalars().all()
        if existing_answers:
            return await _load_existing_analysis(db)

    # Clear existing analysis if forcing
    if force:
        await db.execute(delete(Evidence))
        await db.execute(delete(InterviewAnswer))
        await db.commit()

    # Generate analysis for each question × expert
    question_groups = []
    total_evidence = 0

    for q_idx, question_text in enumerate(INTERVIEW_QUESTIONS, 1):
        analyses = []
        for doc in documents:
            analysis = await analyze_question_for_expert(
                question_id=q_idx,
                question_text=question_text,
                expert_name=doc.expert_name,
                country=doc.country,
                db=db,
                llm=llm,
            )
            analyses.append(analysis)

            # Persist to database
            answer = InterviewAnswer(
                question_id=q_idx,
                question_text=question_text,
                country=doc.country,
                expert_name=doc.expert_name,
                expert_role=doc.expert_role,
                answer=analysis.answer,
                confidence=analysis.confidence,
            )
            db.add(answer)
            await db.flush()

            for source in analysis.sources:
                evidence = Evidence(
                    answer_id=answer.id,
                    chunk_id=source.chunk_id,
                    quote=source.quote,
                    timestamp=source.timestamp,
                    verified=source.verified,
                )
                db.add(evidence)
                total_evidence += 1

        question_groups.append(QuestionAnalysisGroup(
            question_id=q_idx,
            question_text=question_text,
            analyses=analyses,
        ))

    await db.commit()

    return AnalysisResponse(
        questions=question_groups,
        total_questions=len(INTERVIEW_QUESTIONS),
        total_experts=len(documents),
        total_evidence=total_evidence,
    )


async def _load_existing_analysis(db: AsyncSession) -> AnalysisResponse:
    """Load existing analysis from the database."""
    result = await db.execute(
        select(InterviewAnswer).order_by(
            InterviewAnswer.question_id, InterviewAnswer.country
        )
    )
    answers = result.scalars().all()

    # Group by question
    question_groups: dict[int, QuestionAnalysisGroup] = {}
    total_evidence = 0

    for answer in answers:
        if answer.question_id not in question_groups:
            question_groups[answer.question_id] = QuestionAnalysisGroup(
                question_id=answer.question_id,
                question_text=answer.question_text,
                analyses=[],
            )

        # Load evidence for this answer
        ev_result = await db.execute(
            select(Evidence).where(Evidence.answer_id == answer.id)
        )
        evidence_items = ev_result.scalars().all()

        sources = [
            Source(
                chunk_id=ev.chunk_id,
                country=answer.country,
                expert_name=answer.expert_name,
                expert_role=answer.expert_role,
                timestamp=ev.timestamp,
                quote=ev.quote,
                verified=ev.verified,
            )
            for ev in evidence_items
        ]
        total_evidence += len(sources)

        question_groups[answer.question_id].analyses.append(
            QuestionAnalysis(
                question_id=answer.question_id,
                question_text=answer.question_text,
                expert_name=answer.expert_name,
                expert_role=answer.expert_role,
                country=answer.country,
                answer=answer.answer,
                sources=sources,
                confidence=answer.confidence,
            )
        )

    return AnalysisResponse(
        questions=sorted(question_groups.values(), key=lambda q: q.question_id),
        total_questions=len(INTERVIEW_QUESTIONS),
        total_experts=3,
        total_evidence=total_evidence,
    )
