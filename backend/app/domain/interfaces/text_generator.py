"""
Text Generator Interface.
Defines the contract for text generation providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ITextGenerator(ABC):
    """
    Interface for text generation providers.
    Implementations: Gemini 3 Pro, OpenAI, Anthropic, Local LLM
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate text based on prompt and parameters.

        Args:
            prompt: The text prompt for generation
            max_tokens: Maximum tokens to generate
            temperature: Creativity parameter (0.0-1.0)
            context: Additional context for generation

        Returns:
            Generated text string
        """
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        output_schema: Dict[str, Any],
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Generate structured output matching schema.

        Args:
            prompt: The text prompt for generation
            output_schema: JSON schema for output structure
            max_tokens: Maximum tokens to generate

        Returns:
            Structured data matching the schema
        """
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model identifier."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass