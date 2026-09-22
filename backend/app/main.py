"""
ExpertLens AI — FastAPI Application

Evidence-Grounded Expert Interview Intelligence Platform.
Analyzes expert interview transcripts and converts them into
structured, evidence-backed market intelligence.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api import transcripts, analysis, chat, evidence
from app.llm.factory import get_llm_provider


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    await init_db()
    
    # Log provider info
    provider = get_llm_provider()
    print(f"\n{'='*50}")
    print(f"  ExpertLens AI — {settings.APP_VERSION}")
    print(f"  LLM Provider: {provider.provider_name}")
    print(f"  Database: {settings.DATABASE_URL}")
    print(f"{'='*50}\n")
    
    yield
    
    # Shutdown
    print("ExpertLens AI shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Evidence-Grounded Expert Interview Intelligence Platform",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(transcripts.router)
app.include_router(analysis.router)
app.include_router(chat.router)
app.include_router(evidence.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    provider = get_llm_provider()
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_provider": provider.provider_name,
    }
