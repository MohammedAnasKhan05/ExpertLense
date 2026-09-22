"""
ExpertLens AI — Groq LLM Provider

Integrates with the Groq API for fast LLM inference.
"""

from groq import AsyncGroq

from app.llm.base import LLMProvider
from app.config import settings


class GroqProvider(LLMProvider):
    """Groq API LLM provider."""

    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=4096,
        )
        return response.choices[0].message.content or ""

    async def generate_structured(
        self, prompt: str, system_prompt: str = "", schema_hint: str = ""
    ) -> str:
        full_system = system_prompt
        if schema_hint:
            full_system += f"\n\nYou MUST respond with valid JSON matching this schema:\n{schema_hint}"
        
        messages = []
        if full_system:
            messages.append({"role": "system", "content": full_system})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or "{}"

    @property
    def provider_name(self) -> str:
        return f"Groq ({self.model})"
