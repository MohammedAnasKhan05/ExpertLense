"""
ExpertLens AI — Analysis Runner Script

Runs the analysis pipeline for all questions across all experts,
extracts themes, and verifies quotes.

Usage:
    cd backend
    python -m scripts.run_analysis
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import async_session
from app.services.analysis import analyze_all_questions
from app.services.themes import extract_themes
from app.services.comparison import get_comparison
from app.llm import get_llm_provider


async def main():
    print("=" * 60)
    print("  ExpertLens AI — Running Analysis Pipeline")
    print("=" * 60)

    provider = get_llm_provider()
    print(f"Using LLM Provider: {provider.name}")

    async with async_session() as db:
        print("[1/3] Analyzing all 6 questions for all 3 experts...")
        result = await analyze_all_questions(db, provider, force=True)
        print(f"      Total questions: {result.total_questions}")
        print(f"      Total evidence citations: {result.total_evidence}")

        print("[2/3] Extracting cross-expert themes...")
        themes_res = await extract_themes(db, provider)
        print(f"      Themes identified: {len(themes_res.themes)}")
        for t in themes_res.themes:
            print(f"        • [{t.theme_type.upper()}] {t.name}")

        print("[3/3] Generating comparison matrix...")
        comparison = await get_comparison(db)
        print(f"      Comparison topics: {len(comparison.rows)}")

    print()
    print("=" * 60)
    print("  Analysis Pipeline Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
