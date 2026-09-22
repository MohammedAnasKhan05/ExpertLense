"""
ExpertLens AI — Themes Service

Extracts cross-expert themes from transcript analysis.
Identifies common themes and areas of different emphasis.
Never manufactures disagreements.
"""

import json
import logging

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.theme import Theme, ThemeEvidence
from app.services.retrieval import retrieve_for_question, format_context_for_llm
from app.services.quote_validator import validate_quote
from app.llm.base import LLMProvider
from app.schemas.theme import ThemeSchema, ThemeEvidenceSchema, ThemesResponse

logger = logging.getLogger(__name__)

THEME_TOPICS = [
    "Capital budgets and economic considerations in robotic surgery adoption",
    "Surgeon training and utilisation requirements",
    "Clinical outcomes and their role in purchasing decisions",
    "Uneven adoption across hospital types and regions",
    "Procedure volume and system utilisation",
    "Purchasing timelines and decision-making processes",
    "Future adoption outlook and growth expectations",
]

THEME_SYSTEM_PROMPT = """You are an expert research analyst identifying themes across expert interviews.

CRITICAL RULES:
1. Only identify themes supported by transcript evidence
2. Classify as "common_theme" when experts agree or say similar things
3. Classify as "different_emphasis" only when experts genuinely focus on different aspects
4. NEVER use "disagreement" unless experts explicitly contradict each other
5. Include exact quotes as evidence
6. Never invent information

Respond with valid JSON:
{
    "themes": [
        {
            "theme_name": "Short descriptive name",
            "description": "What this theme captures across experts",
            "theme_type": "common_theme|different_emphasis",
            "evidence": [
                {
                    "expert_name": "name",
                    "country": "country",
                    "quote": "exact quote",
                    "timestamp": "timestamp",
                    "chunk_id": "chunk_id"
                }
            ]
        }
    ]
}"""


async def extract_themes(
    db: AsyncSession,
    llm: LLMProvider,
    force: bool = False,
) -> ThemesResponse:
    """
    Extract cross-expert themes from transcript evidence.
    
    Args:
        db: Database session
        llm: LLM provider
        force: If True, regenerate themes
        
    Returns:
        ThemesResponse with identified themes and evidence
    """
    # Check for existing themes
    if not force:
        existing = await db.execute(select(Theme))
        existing_themes = existing.scalars().all()
        if existing_themes:
            return await _load_existing_themes(db)

    # Clear existing
    if force:
        await db.execute(delete(ThemeEvidence))
        await db.execute(delete(Theme))
        await db.commit()

    # Get all documents for reference
    doc_result = await db.execute(select(Document))
    documents = doc_result.scalars().all()

    if not documents:
        return ThemesResponse(themes=[], common_themes=0, different_emphasis=0)

    # Gather evidence across all topics
    all_context_parts = []
    all_chunks = []
    
    for topic in THEME_TOPICS:
        chunks = await retrieve_for_question(
            question=topic,
            db=db,
            top_k=6,
        )
        all_chunks.extend(chunks)
        if chunks:
            all_context_parts.append(format_context_for_llm(chunks))

    if not all_context_parts:
        return ThemesResponse(themes=[], common_themes=0, different_emphasis=0)

    # Build prompt
    combined_context = "\n\n".join(all_context_parts)
    prompt = f"""Analyze the following expert transcript evidence and identify recurring themes.

The experts are from France, Germany, and United Kingdom discussing robotic surgery adoption.

Transcript evidence:
{combined_context}

Identify 5-8 key themes. For each theme:
- Determine if it's a "common_theme" (experts agree) or "different_emphasis" (experts focus on different aspects)
- Include exact quotes from at least 2 experts as evidence
- Never manufacture disagreements"""

    # Get LLM response
    try:
        response_text = await llm.generate_structured(prompt, THEME_SYSTEM_PROMPT)
        response_data = json.loads(response_text)
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Theme extraction LLM failed: {e}")
        response_data = {}

    if not response_data.get("themes"):
        response_data = _generate_fallback_themes(all_chunks)

    # Process and validate themes
    themes_list = []
    all_source_text = " ".join(c["text"] for c in all_chunks)

    for theme_data in response_data.get("themes", []):
        theme = Theme(
            theme_name=theme_data.get("theme_name", ""),
            description=theme_data.get("description", ""),
            theme_type=theme_data.get("theme_type", "common_theme"),
        )
        db.add(theme)
        await db.flush()

        evidence_schemas = []
        for ev in theme_data.get("evidence", []):
            quote = ev.get("quote", "")
            if not quote:
                continue

            # Find matching chunk first
            matching_chunk = next(
                (c for c in all_chunks if quote.lower()[:25] in c["text"].lower() or c["text"].lower()[:25] in quote.lower()),
                None
            )
            chunk_id = matching_chunk["chunk_id"] if matching_chunk else ev.get("chunk_id", "")
            exp_name = ev.get("expert_name") or (matching_chunk["expert_name"] if matching_chunk else "")
            c_country = ev.get("country") or (matching_chunk["country"] if matching_chunk else "")
            ts = ev.get("timestamp") or (matching_chunk["timestamp"] if matching_chunk else "")

            # Validate quote
            is_valid = validate_quote(quote, all_source_text)
            final_quote = quote if is_valid else (matching_chunk["text"] if matching_chunk else quote)

            te = ThemeEvidence(
                theme_id=theme.id,
                chunk_id=chunk_id,
                expert_name=exp_name,
                country=c_country,
                quote=final_quote,
                timestamp=ts,
            )
            db.add(te)
            evidence_schemas.append(ThemeEvidenceSchema(
                chunk_id=chunk_id,
                expert_name=exp_name,
                country=c_country,
                quote=final_quote,
                timestamp=ts,
            ))

        themes_list.append(ThemeSchema(
            id=theme.id,
            theme_name=theme.theme_name,
            description=theme.description,
            theme_type=theme.theme_type,
            evidence=evidence_schemas,
            expert_count=len(set(e.expert_name for e in evidence_schemas)),
        ))

    await db.commit()

    common = sum(1 for t in themes_list if t.theme_type == "common_theme")
    diff = sum(1 for t in themes_list if t.theme_type == "different_emphasis")

    return ThemesResponse(
        themes=themes_list,
        common_themes=common,
        different_emphasis=diff,
    )


def _generate_fallback_themes(chunks: list[dict]) -> dict:
    """Generate fallback themes from raw chunks without LLM."""
    topic_keywords = {
        "Capital Budgets & Economic Feasibility": ["budget", "capital", "cost", "economic", "finance", "roi", "price", "reimbursement"],
        "Surgeon Training Capacity & Utilisation": ["training", "surgeon", "utilisation", "utilization", "staff", "theatre"],
        "Clinical Outcomes & Patient Length of Stay": ["clinical", "outcome", "patient", "stay", "complication"],
        "Uneven Adoption Across Hospital Segments": ["adoption", "growing", "increasing", "uneven", "segment", "university"],
        "Procedure Volume as Adoption Prerequisite": ["procedure", "volume", "case", "sustainable"],
        "Multi-Stakeholder Purchasing Cycles": ["purchase", "timeline", "months", "procurement", "cycle"],
        "Long-term Technology Expansion Outlook": ["expect", "future", "outlook", "trend", "growth", "accelerate"],
    }

    themes = []
    for theme_name, keywords in topic_keywords.items():
        evidence = []
        for chunk in chunks:
            text_lower = chunk.get("text", "").lower()
            if any(kw in text_lower for kw in keywords):
                if not any(e["chunk_id"] == chunk.get("chunk_id") for e in evidence):
                    evidence.append({
                        "expert_name": chunk.get("expert_name", ""),
                        "country": chunk.get("country", ""),
                        "quote": chunk.get("text", ""),
                        "timestamp": chunk.get("timestamp", ""),
                        "chunk_id": chunk.get("chunk_id", ""),
                    })

        if len(evidence) >= 2:
            experts = set(e["expert_name"] for e in evidence if e["expert_name"])
            themes.append({
                "theme_name": theme_name,
                "description": f"Analyzed across {len(experts)} market perspectives: {', '.join(sorted(experts))}.",
                "theme_type": "common_theme" if len(experts) >= 2 else "different_emphasis",
                "evidence": evidence[:4],
            })

    return {"themes": themes}


async def _load_existing_themes(db: AsyncSession) -> ThemesResponse:
    """Load existing themes from database."""
    result = await db.execute(select(Theme))
    themes = result.scalars().all()

    theme_schemas = []
    for theme in themes:
        ev_result = await db.execute(
            select(ThemeEvidence).where(ThemeEvidence.theme_id == theme.id)
        )
        evidence = ev_result.scalars().all()

        theme_schemas.append(ThemeSchema(
            id=theme.id,
            theme_name=theme.theme_name,
            description=theme.description,
            theme_type=theme.theme_type,
            evidence=[
                ThemeEvidenceSchema(
                    chunk_id=ev.chunk_id,
                    expert_name=ev.expert_name,
                    country=ev.country,
                    quote=ev.quote,
                    timestamp=ev.timestamp,
                )
                for ev in evidence
            ],
            expert_count=len(set(ev.expert_name for ev in evidence)),
        ))

    common = sum(1 for t in theme_schemas if t.theme_type == "common_theme")
    diff = sum(1 for t in theme_schemas if t.theme_type == "different_emphasis")

    return ThemesResponse(
        themes=theme_schemas,
        common_themes=common,
        different_emphasis=diff,
    )
