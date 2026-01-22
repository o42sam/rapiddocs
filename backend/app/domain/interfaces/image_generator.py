"""
Image Generator Interface.
Defines the contract for image generation providers.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from pathlib import Path


class IImageGenerator(ABC):
    """
    Interface for image generation providers.
    Implementations: Nano Banana, FLUX, Stable Diffusion, DALL-E
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        style_hints: Optional[str] = None
    ) -> bytes:
        """
        Generate image and return as bytes.

        Args:
            prompt: Text description of the image to generate
            width: Image width in pixels
            height: Image height in pixels
            style_hints: Additional style guidance

        Returns:
            Generated image as bytes
        """
        pass

    @abstractmethod
    async def generate_batch(
        self,
        prompts: List[str],
        width: int = 512,
        height: int = 512
    ) -> List[bytes]:
        """
        Generate multiple images.

        Args:
            prompts: List of text descriptions
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            List of generated images as bytes
        """
        pass

    @abstractmethod
    async def generate_to_file(
        self,
        prompt: str,
        output_path: Path,
        width: int = 512,
        height: int = 512
    ) -> Path:
        """
        Generate image and save to file.

        Args:
            prompt: Text description of the image
            output_path: Path to save the image
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            Path to the saved image
        """
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model identifier."""
        pass