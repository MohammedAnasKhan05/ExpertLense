"""
ExpertLens AI — HuggingFace LLM Provider

Integrates with the HuggingFace Inference API.
"""

from huggingface_hub import AsyncInferenceClient

from app.llm.base import LLMProvider
from app.config import settings


class HuggingFaceProvider(LLMProvider):
    """HuggingFace Inference API LLM provider."""

    def __init__(self):
        self.client = AsyncInferenceClient(
            model=settings.HF_MODEL,
            token=settings.HF_TOKEN,
        )
        self.model = settings.HF_MODEL

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        full_prompt = ""
        if system_prompt:
            full_prompt = f"[INST] {system_prompt}\n\n{prompt} [/INST]"
        else:
            full_prompt = f"[INST] {prompt} [/INST]"

        response = await self.client.text_generation(
            full_prompt,
            max_new_tokens=4096,
            temperature=0.1,
        )
        return response

    async def generate_structured(
        self, prompt: str, system_prompt: str = "", schema_hint: str = ""
    ) -> str:
        full_system = system_prompt or ""
        if schema_hint:
            full_system += f"\n\nYou MUST respond with valid JSON matching this schema:\n{schema_hint}"
        full_system += "\n\nRespond ONLY with valid JSON. No other text."

        return await self.generate(prompt, full_system)

    @property
    def provider_name(self) -> str:
        return f"HuggingFace ({self.model})"
