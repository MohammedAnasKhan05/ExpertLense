"""
ExpertLens AI — LLM Provider Factory

Returns the appropriate LLM provider based on configuration.
"""

import logging
from app.config import settings
from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)


def get_llm_provider() -> LLMProvider:
    """
    Factory function that returns the configured LLM provider.
    
    Reads LLM_PROVIDER from settings and returns the appropriate instance.
    Falls back to LocalProvider if the requested provider can't be initialized.
    """
    provider = (settings.LLM_PROVIDER or "local").lower().strip()

    if provider == "groq":
        if not settings.GROQ_API_KEY:
            logger.warning("LLM_PROVIDER is set to 'groq' but GROQ_API_KEY is empty. Falling back to LocalProvider.")
        else:
            try:
                from app.llm.groq_provider import GroqProvider
                return GroqProvider()
            except Exception as e:
                logger.error(f"Failed to initialize GroqProvider: {e}. Falling back to LocalProvider.")

    elif provider == "huggingface":
        if not settings.HF_TOKEN:
            logger.warning("LLM_PROVIDER is set to 'huggingface' but HF_TOKEN is empty. Falling back to LocalProvider.")
        else:
            try:
                from app.llm.huggingface_provider import HuggingFaceProvider
                return HuggingFaceProvider()
            except Exception as e:
                logger.error(f"Failed to initialize HuggingFaceProvider: {e}. Falling back to LocalProvider.")

    from app.llm.local_provider import LocalProvider
    return LocalProvider()

