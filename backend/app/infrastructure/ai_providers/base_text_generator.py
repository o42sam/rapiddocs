"""
Base Text Generator Implementation.
Abstract base class for text generation providers.
"""

from abc import ABC
from typing import Dict, Any, Optional
import logging

from ...domain.interfaces.text_generator import ITextGenerator

logger = logging.getLogger(__name__)


class BaseTextGenerator(ITextGenerator, ABC):
    """
    Base implementation for text generators with common functionality.

    This class provides common functionality that can be shared
    across different text generation implementations.
    """

    def __init__(self, model_name: str, provider_name: str):
        """
        Initialize base text generator.

        Args:
            model_name: Name/ID of the model
            provider_name: Name of the provider (e.g., "Gemini", "OpenAI")
        """
        self._model_name = model_name
        self._provider_name = provider_name
        logger.info(f"Initialized {provider_name} text generator with model: {model_name}")

    @property
    def model_name(self) -> str:
        """Return the model identifier."""
        return self._model_name

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return self._provider_name

    def _clean_generated_text(self, text: str) -> str:
        """
        Clean up generated text.

        Args:
            text: Raw generated text

        Returns:
            Cleaned text
        """
        # Remove leading/trailing whitespace
        text = text.strip()

        # Remove excessive newlines (more than 2 consecutive)
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')

        return text

    def _validate_parameters(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> None:
        """
        Validate generation parameters.

        Args:
            prompt: The prompt text
            max_tokens: Maximum tokens to generate
            temperature: Temperature parameter

        Raises:
            ValueError: If parameters are invalid
        """
        if not prompt:
            raise ValueError("Prompt cannot be empty")

        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        if not 0.0 <= temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")

    def _log_generation_stats(
        self,
        prompt: str,
        generated_text: str,
        generation_time: float
    ) -> None:
        """
        Log generation statistics.

        Args:
            prompt: The input prompt
            generated_text: The generated text
            generation_time: Time taken for generation in seconds
        """
        prompt_tokens = len(prompt.split())
        generated_tokens = len(generated_text.split())

        logger.info(
            f"Text generation completed - "
            f"Provider: {self._provider_name}, "
            f"Model: {self._model_name}, "
            f"Prompt tokens: {prompt_tokens}, "
            f"Generated tokens: {generated_tokens}, "
            f"Time: {generation_time:.2f}s"
        )