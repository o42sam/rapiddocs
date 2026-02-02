"""
Base Image Generator.
Abstract base class for image generation providers.
"""

from abc import ABC
from typing import Optional, List
from pathlib import Path
import logging

from ...domain.interfaces.image_generator import IImageGenerator

logger = logging.getLogger(__name__)


class BaseImageGenerator(IImageGenerator, ABC):
    """
    Abstract base class for image generators.
    Provides common functionality and validation.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "default"):
        """
        Initialize base image generator.

        Args:
            api_key: API key for the provider
            model: Model identifier
        """
        self._api_key = api_key
        self._model = model
        self._is_active = False

    @property
    def is_active(self) -> bool:
        """Check if the generator is active and ready."""
        return self._is_active

    @property
    def model_name(self) -> str:
        """Return the model identifier."""
        return self._model

    def _validate_dimensions(self, width: int, height: int) -> tuple:
        """
        Validate and adjust image dimensions.

        Args:
            width: Requested width
            height: Requested height

        Returns:
            Tuple of validated (width, height)
        """
        # Ensure dimensions are positive
        width = max(64, min(width, 2048))
        height = max(64, min(height, 2048))

        # Round to nearest multiple of 8 (common requirement)
        width = (width // 8) * 8
        height = (height // 8) * 8

        return width, height

    def _validate_prompt(self, prompt: str) -> str:
        """
        Validate and clean the prompt.

        Args:
            prompt: Input prompt

        Returns:
            Cleaned prompt
        """
        # Remove excessive whitespace
        prompt = ' '.join(prompt.split())

        # Truncate if too long (most APIs have limits)
        max_length = 500
        if len(prompt) > max_length:
            prompt = prompt[:max_length]
            logger.warning(f"Prompt truncated to {max_length} characters")

        return prompt

    def _ensure_output_directory(self, output_path: Path) -> None:
        """
        Ensure the output directory exists.

        Args:
            output_path: Path where image will be saved
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

    async def generate_batch(
        self,
        prompts: List[str],
        width: int = 512,
        height: int = 512
    ) -> List[bytes]:
        """
        Generate multiple images.
        Default implementation calls generate() for each prompt.

        Args:
            prompts: List of text descriptions
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            List of generated images as bytes
        """
        results = []
        for prompt in prompts:
            try:
                image_bytes = await self.generate(prompt, width, height)
                results.append(image_bytes)
            except Exception as e:
                logger.error(f"Failed to generate image for prompt: {e}")
                # Return empty bytes for failed generations
                results.append(b'')
        return results

    async def generate_to_file(
        self,
        prompt: str,
        output_path: Path,
        width: int = 512,
        height: int = 512
    ) -> Path:
        """
        Generate image and save to file.
        Default implementation calls generate() and saves the result.

        Args:
            prompt: Text description of the image
            output_path: Path to save the image
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            Path to the saved image
        """
        self._ensure_output_directory(output_path)

        image_bytes = await self.generate(prompt, width, height)

        if image_bytes:
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
            logger.info(f"Image saved to: {output_path}")
        else:
            logger.warning(f"No image data to save for: {output_path}")

        return output_path
