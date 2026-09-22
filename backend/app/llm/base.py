"""
ExpertLens AI — LLM Provider Base

Abstract base class for all LLM providers.
The rest of the application depends only on this interface.
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract LLM provider interface."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Generate a text response from the LLM.
        
        Args:
            prompt: The user/task prompt
            system_prompt: System-level instructions
            
        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    async def generate_structured(
        self, prompt: str, system_prompt: str = "", schema_hint: str = ""
    ) -> str:
        """
        Generate a structured (JSON) response from the LLM.
        
        Args:
            prompt: The user/task prompt
            system_prompt: System-level instructions
            schema_hint: JSON schema description for the expected output
            
        Returns:
            JSON string response
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider."""
        pass

    @property
    def name(self) -> str:
        """Alias for provider_name."""
        return self.provider_name
