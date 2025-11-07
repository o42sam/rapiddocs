import requests
import io
from PIL import Image
from typing import Tuple
from app.config import settings
from app.utils.logger import get_logger
from app.utils.exceptions import ImageGenerationError

logger = get_logger('image_generation')


class ImageGenerationService:
    def __init__(self):
        self.api_url = f"https://api-inference.huggingface.co/models/{settings.IMAGE_GENERATION_MODEL}"
        self.headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}

    def _build_prompt(
        self,
        document_theme: str,
        color1: str,
        color2: str,
        image_number: int = 1
    ) -> str:
        """Build prompt for image generation"""
        prompts = [
            f"Professional business illustration about {document_theme}, clean modern corporate style, color palette {color1} and {color2}, high quality",
            f"Abstract business concept art for {document_theme}, minimalist design, professional, colors {color1} {color2}",
            f"Modern infographic style illustration representing {document_theme}, clean professional design, {color1} {color2} color scheme"
        ]

        return prompts[min(image_number - 1, len(prompts) - 1)]

    def generate_image(
        self,
        document_theme: str,
        color1: str,
        color2: str,
        image_number: int = 1,
        max_retries: int = 3
    ) -> bytes:
        """
        Generate an image using Hugging Face API

        Args:
            document_theme: Theme or description for the image
            color1: Primary color for the image
            color2: Secondary color for the image
            image_number: Image sequence number
            max_retries: Maximum retry attempts

        Returns:
            Image data as bytes

        Raises:
            ImageGenerationError: If image generation fails
        """
        try:
            logger.info(f"Generating image #{image_number} for theme: {document_theme[:50]}...")

            prompt = self._build_prompt(document_theme, color1, color2, image_number)
            logger.debug(f"Image generation prompt: {prompt}")

            payload = {
                "inputs": prompt,
                "parameters": {
                    "num_inference_steps": 4,  # FLUX.1-schnell is optimized for 4 steps
                    "guidance_scale": 0.0  # FLUX.1-schnell doesn't use guidance
                }
            }

            for attempt in range(max_retries):
                try:
                    logger.debug(f"Image generation attempt {attempt + 1}/{max_retries}")

                    response = requests.post(
                        self.api_url,
                        headers=self.headers,
                        json=payload,
                        timeout=60
                    )

                    if response.status_code == 503:
                        # Model is loading, wait and retry
                        logger.warning(f"Model loading (503), waiting 20 seconds before retry...")
                        import time
                        time.sleep(20)
                        continue

                    response.raise_for_status()

                    # Response should be image bytes
                    image_bytes = response.content
                    logger.debug(f"Received {len(image_bytes)} bytes from API")

                    # Validate it's an actual image
                    try:
                        img = Image.open(io.BytesIO(image_bytes))
                        img.verify()
                        logger.info(f"Image #{image_number} generated successfully")
                        return image_bytes
                    except Exception as e:
                        logger.error(f"Invalid image data received: {str(e)}")
                        raise ImageGenerationError(
                            f"Invalid image data received: {str(e)}",
                            details={'image_number': image_number, 'data_size': len(image_bytes)}
                        )

                except requests.exceptions.Timeout:
                    logger.warning(f"Image generation timeout (attempt {attempt + 1}/{max_retries})")
                    if attempt == max_retries - 1:
                        raise ImageGenerationError(
                            "Image generation timed out after multiple attempts",
                            details={'image_number': image_number, 'max_retries': max_retries}
                        )
                    continue

                except requests.exceptions.RequestException as e:
                    logger.error(f"Request error during image generation: {str(e)}")
                    if attempt == max_retries - 1:
                        raise ImageGenerationError(
                            f"Image generation request failed: {str(e)}",
                            details={'image_number': image_number, 'attempt': attempt + 1}
                        )
                    continue

            raise ImageGenerationError(
                "Image generation failed after all retries",
                details={'image_number': image_number, 'max_retries': max_retries}
            )

        except ImageGenerationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in image generation: {str(e)}", exc_info=True)
            raise ImageGenerationError(
                f"Unexpected error in image generation: {str(e)}",
                details={'image_number': image_number}
            )

    def generate_multiple_images(
        self,
        document_theme: str,
        color1: str,
        color2: str,
        count: int = 2
    ) -> list[bytes]:
        """
        Generate multiple images for a document

        Args:
            document_theme: Theme or description for the images
            color1: Primary color
            color2: Secondary color
            count: Number of images to generate (max 3)

        Returns:
            List of image data as bytes

        Note:
            This method continues generating remaining images even if one fails
        """
        logger.info(f"Generating {count} images for document theme")
        images = []
        errors = []

        for i in range(min(count, 3)):  # Max 3 images
            try:
                image_bytes = self.generate_image(
                    document_theme,
                    color1,
                    color2,
                    image_number=i + 1
                )
                images.append(image_bytes)
            except ImageGenerationError as e:
                logger.error(f"Failed to generate image {i+1}: {e.message}")
                errors.append(f"Image {i+1}: {e.message}")
                # Continue with other images even if one fails
            except Exception as e:
                logger.error(f"Unexpected error generating image {i+1}: {str(e)}")
                errors.append(f"Image {i+1}: {str(e)}")

        logger.info(f"Successfully generated {len(images)}/{count} images")

        if errors:
            logger.warning(f"Errors encountered: {'; '.join(errors)}")

        return images

    def resize_image(self, image_bytes: bytes, max_width: int = 800) -> bytes:
        """Resize image to fit in PDF"""
        img = Image.open(io.BytesIO(image_bytes))

        # Calculate new size maintaining aspect ratio
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # Save to bytes
        output = io.BytesIO()
        img.save(output, format='PNG')
        return output.getvalue()


image_generation_service = ImageGenerationService()
