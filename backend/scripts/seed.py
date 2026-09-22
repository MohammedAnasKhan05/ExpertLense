"""
ExpertLens AI — Data Seeding Script

Loads the three demo transcripts, parses, chunks, stores in SQL,
generates embeddings, and indexes in ChromaDB.

Usage:
    cd backend
    python -m scripts.seed
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, async_session
from app.services.ingestion import ingest_from_directory
from app.config import settings


async def seed():
    """Run the full seeding pipeline."""
    print("=" * 50)
    print("  ExpertLens AI — Data Seeding")
    print("=" * 50)
    print()

    # Initialize database
    print("[1/3] Initializing database...")
    await init_db()
    print("      [OK] Database tables created")

    # Ingest transcripts
    print(f"[2/3] Ingesting transcripts from: {settings.TRANSCRIPTS_DIR}")
    
    async with async_session() as db:
        try:
            results = await ingest_from_directory(settings.TRANSCRIPTS_DIR, db)
        except FileNotFoundError:
            print(f"      [FAIL] Directory not found: {settings.TRANSCRIPTS_DIR}")
            print(f"      Make sure transcript files are in the data/transcripts/ directory")
            sys.exit(1)

    # Report results
    print(f"[3/3] Results:")
    total_chunks = 0
    for r in results:
        if "error" in r:
            print(f"      [FAIL] {r.get('filename', 'unknown')}: {r['error']}")
        else:
            chunks = r.get('chunks_created', 0)
            total_chunks += chunks
            status = "[OK] Ingested" if chunks > 0 else "[SKIP] Already exists"
            print(f"      {status}: {r['expert_name']} ({r['country']}) — {chunks} chunks")

    print()
    print("=" * 50)
    print(f"  Seeding complete!")
    print(f"  Documents: {len(results)}")
    print(f"  Chunks created: {total_chunks}")
    print("=" * 50)
    print()
    print("Next steps:")
    print("  1. Start the backend:  uvicorn app.main:app --reload")
    print("  2. Start the frontend: cd ../frontend && npm run dev")
    print("  3. Trigger analysis:   POST http://localhost:8000/api/analysis/analyze")


if __name__ == "__main__":
    asyncio.run(seed())
