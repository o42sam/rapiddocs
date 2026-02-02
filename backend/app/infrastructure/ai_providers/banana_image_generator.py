"""
Banana/HuggingFace Image Generator Implementation.
Implements IImageGenerator interface using HuggingFace Inference API.
"""

import os
import io
import asyncio
from typing import Optional, List
from pathlib import Path

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    aiohttp = None
    AIOHTTP_AVAILABLE = False

from PIL import Image

from .base_image_generator import BaseImageGenerator
from ...shared.logger import get_logger

logger = get_logger("banana_image_generator")


class BananaImageGenerator(BaseImageGenerator):
    """
    HuggingFace/Banana implementation of image generation.
    Uses HuggingFace Inference API with FLUX or similar models.

    Features:
    - Async image generation
    - Batch processing support
    - Automatic retry logic
    - Fallback placeholder generation
    - Comprehensive logging
    """

    # Default model (FLUX.1 schnell is fast and high quality)
    DEFAULT_MODEL = "black-forest-labs/FLUX.1-schnell"

    # Alternative models to try
    FALLBACK_MODELS = [
        "stabilityai/stable-diffusion-xl-base-1.0",
        "runwayml/stable-diffusion-v1-5",
        "CompVis/stable-diffusion-v1-4"
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120
    ):
        """
        Initialize the Banana/HuggingFace image generator.

        Args:
            api_key: HuggingFace API key (falls back to environment variable)
            model: Model identifier (defaults to FLUX.1-schnell)
            timeout: Request timeout in seconds
        """
        self._api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        self._model = model or os.getenv("IMAGE_GENERATION_MODEL", self.DEFAULT_MODEL)
        self._timeout = timeout
        self._is_active = False
        self._current_model = self._model

        self._initialize()

    def _initialize(self) -> None:
        """Initialize the image generator with comprehensive logging."""
        logger.info("=" * 60)
        logger.info("BANANA/HUGGINGFACE IMAGE GENERATOR INITIALIZATION")
        logger.info("=" * 60)

        if not AIOHTTP_AVAILABLE:
            logger.warning("aiohttp package not installed")
            logger.warning("Image generation will use placeholder images")
            logger.info("MODEL STATUS: INACTIVE (Package not installed)")
            logger.info("To enable: pip install aiohttp")
            self._is_active = False
            return

        if not self._api_key:
            logger.warning("No HuggingFace API key found")
            logger.warning("Image generation will use placeholder images")
            logger.info("MODEL STATUS: INACTIVE (No API Key)")
            logger.info("To enable: Set HUGGINGFACE_API_KEY environment variable")
            self._is_active = False
        else:
            logger.info(f"API Key: {'*' * 8}...{self._api_key[-4:] if len(self._api_key) > 4 else '****'}")
            logger.info(f"Primary Model: {self._model}")
            logger.info(f"Timeout: {self._timeout}s")
            logger.info("MODEL STATUS: ACTIVE")
            self._is_active = True

        logger.info("=" * 60)

    @property
    def is_active(self) -> bool:
        """Check if the generator is active."""
        return self._is_active

    @property
    def model_name(self) -> str:
        """Return the current model identifier."""
        return self._current_model

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "HuggingFace/Banana"

    def _get_api_url(self, model: str) -> str:
        """Get the API URL for a model."""
        return f"https://api-inference.huggingface.co/models/{model}"

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
            Generated image as bytes (PNG format)
        """
        logger.info(f"Image generation requested - Model active: {self._is_active}")
        logger.debug(f"Prompt: {prompt[:100]}...")

        if not self._is_active:
            logger.warning("Model inactive, generating placeholder image")
            return self._generate_placeholder(prompt, width, height)

        # Validate and enhance prompt
        enhanced_prompt = self._enhance_prompt(prompt, style_hints)
        width, height = self._validate_dimensions(width, height)

        # Try primary model first, then fallbacks
        models_to_try = [self._model] + self.FALLBACK_MODELS
        last_error = None

        for model in models_to_try:
            try:
                logger.info(f"Attempting generation with model: {model}")
                image_bytes = await self._generate_with_model(model, enhanced_prompt, width, height)

                if image_bytes:
                    self._current_model = model
                    logger.info(f"Generation successful with {model}")
                    return image_bytes

            except Exception as e:
                logger.warning(f"Model {model} failed: {e}")
                last_error = e
                continue

        # All models failed, return placeholder
        logger.error(f"All models failed. Last error: {last_error}")
        return self._generate_placeholder(prompt, width, height)

    async def _generate_with_model(
        self,
        model: str,
        prompt: str,
        width: int,
        height: int
    ) -> Optional[bytes]:
        """
        Attempt generation with a specific model.

        Args:
            model: Model identifier
            prompt: Enhanced prompt
            width: Image width
            height: Image height

        Returns:
            Image bytes or None if failed
        """
        if not AIOHTTP_AVAILABLE or aiohttp is None:
            logger.warning("aiohttp not available, cannot generate image")
            return None

        api_url = self._get_api_url(model)
        headers = {"Authorization": f"Bearer {self._api_key}"}

        payload = {
            "inputs": prompt,
            "parameters": {
                "width": width,
                "height": height,
                "num_inference_steps": 25,  # Balance between quality and speed
                "guidance_scale": 7.5
            },
            "options": {
                "wait_for_model": True,
                "use_cache": False
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self._timeout)
            ) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')

                    if 'image' in content_type:
                        # Direct image response
                        return await response.read()
                    elif 'application/json' in content_type:
                        # JSON response (possibly with base64 image)
                        data = await response.json()
                        if isinstance(data, list) and len(data) > 0:
                            # Handle array response format
                            import base64
                            if 'image' in data[0]:
                                return base64.b64decode(data[0]['image'])

                    logger.warning(f"Unexpected response type: {content_type}")
                    return None

                elif response.status == 503:
                    # Model loading, wait and retry
                    logger.info(f"Model {model} is loading, waiting...")
                    data = await response.json()
                    wait_time = data.get('estimated_time', 30)
                    await asyncio.sleep(min(wait_time, 60))

                    # Retry once after waiting
                    async with session.post(
                        api_url,
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=self._timeout)
                    ) as retry_response:
                        if retry_response.status == 200:
                            return await retry_response.read()

                    return None

                else:
                    error_text = await response.text()
                    logger.error(f"API error {response.status}: {error_text[:200]}")
                    raise Exception(f"API error: {response.status}")

    def _enhance_prompt(self, prompt: str, style_hints: Optional[str] = None) -> str:
        """
        Enhance the prompt for better image generation.

        Args:
            prompt: Original prompt
            style_hints: Additional style guidance

        Returns:
            Enhanced prompt
        """
        # Base enhancement for professional infographic images
        enhancements = [
            "professional illustration",
            "clean design",
            "high quality",
            "detailed"
        ]

        enhanced = prompt

        # Add style hints if provided
        if style_hints:
            enhanced = f"{enhanced}, {style_hints}"

        # Add quality enhancements
        if "illustration" not in prompt.lower():
            enhanced = f"{enhanced}, {', '.join(enhancements)}"

        # Validate length
        enhanced = self._validate_prompt(enhanced)

        return enhanced

    def _generate_placeholder(self, prompt: str, width: int, height: int) -> bytes:
        """
        Generate a placeholder image when API is unavailable.

        Args:
            prompt: Original prompt (used for text on image)
            width: Image width
            height: Image height

        Returns:
            PNG image bytes
        """
        logger.info(f"Generating placeholder image: {width}x{height}")

        try:
            # Create a gradient background
            img = Image.new('RGB', (width, height), color='#f0f4f8')

            # Try to add text (requires PIL with font support)
            try:
                from PIL import ImageDraw, ImageFont

                draw = ImageDraw.Draw(img)

                # Draw border
                border_color = '#1e40af'
                draw.rectangle(
                    [10, 10, width - 10, height - 10],
                    outline=border_color,
                    width=3
                )

                # Draw placeholder text
                text = "Image Placeholder"
                try:
                    # Try to use a built-in font
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
                except:
                    font = ImageFont.load_default()

                # Center the text
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                x = (width - text_width) // 2
                y = (height - text_height) // 2

                draw.text((x, y), text, fill='#1e40af', font=font)

                # Add smaller prompt excerpt
                prompt_short = prompt[:50] + "..." if len(prompt) > 50 else prompt
                try:
                    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
                except:
                    small_font = ImageFont.load_default()

                prompt_bbox = draw.textbbox((0, 0), prompt_short, font=small_font)
                prompt_width = prompt_bbox[2] - prompt_bbox[0]
                px = (width - prompt_width) // 2

                draw.text((px, y + 40), prompt_short, fill='#64748b', font=small_font)

            except ImportError:
                pass  # No drawing support, return plain image

            # Convert to bytes
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            return buffer.getvalue()

        except Exception as e:
            logger.error(f"Failed to create placeholder: {e}")
            # Return minimal valid PNG
            return self._minimal_png(width, height)

    def _minimal_png(self, width: int, height: int) -> bytes:
        """Create a minimal valid PNG image."""
        img = Image.new('RGB', (width, height), color='#e5e7eb')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()

    async def generate_batch(
        self,
        prompts: List[str],
        width: int = 512,
        height: int = 512
    ) -> List[bytes]:
        """
        Generate multiple images concurrently.

        Args:
            prompts: List of text descriptions
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            List of generated images as bytes
        """
        logger.info(f"Batch generation requested: {len(prompts)} images")

        # Create tasks for concurrent execution
        tasks = [
            self.generate(prompt, width, height)
            for prompt in prompts
        ]

        # Execute with limited concurrency to avoid rate limits
        results = []
        batch_size = 3  # Process 3 at a time

        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch generation error: {result}")
                    results.append(self._generate_placeholder("Error", width, height))
                else:
                    results.append(result)

            # Small delay between batches to avoid rate limits
            if i + batch_size < len(tasks):
                await asyncio.sleep(1)

        logger.info(f"Batch generation complete: {len(results)} images")
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

        Args:
            prompt: Text description of the image
            output_path: Path to save the image
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            Path to the saved image
        """
        logger.info(f"Generating image to file: {output_path}")

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate image
        image_bytes = await self.generate(prompt, width, height)

        # Save to file
        with open(output_path, 'wb') as f:
            f.write(image_bytes)

        logger.info(f"Image saved: {output_path} ({len(image_bytes)} bytes)")
        return output_path

    def get_status(self) -> dict:
        """Get generator status information."""
        return {
            "provider": self.provider_name,
            "model": self._current_model,
            "primary_model": self._model,
            "is_active": self._is_active,
            "has_api_key": bool(self._api_key),
            "timeout": self._timeout,
            "status": "ACTIVE" if self._is_active else "INACTIVE"
        }
