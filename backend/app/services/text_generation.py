import requests
from typing import List
from app.config import settings
from app.models.document import Statistic
from app.utils.logger import get_logger
from app.utils.exceptions import TextGenerationError

logger = get_logger('text_generation')


class TextGenerationService:
    def __init__(self):
        # Check if HuggingFace API key is available (production) or use Ollama (local dev)
        self.use_huggingface = bool(settings.HUGGINGFACE_API_KEY and settings.HUGGINGFACE_API_KEY != "your-token-here")

        if self.use_huggingface:
            # Production: Use HuggingFace API
            self.api_url = "https://api-inference.huggingface.co/models/" + settings.TEXT_GENERATION_MODEL
            self.model = settings.TEXT_GENERATION_MODEL
            self.headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
            logger.info(f"Initialized TextGenerationService with HuggingFace API: {self.model}")
        else:
            # Development: Use local Ollama API
            self.api_url = "http://localhost:11434/api/generate"
            self.model = "gemma:2b"
            self.headers = {}
            logger.info(f"Initialized TextGenerationService with local Ollama: {self.model}")

        logger.debug(f"API URL: {self.api_url}")

    def _format_statistics(self, statistics: List[Statistic]) -> str:
        """Format statistics for inclusion in prompt"""
        if not statistics:
            return "No specific statistics provided."

        stats_text = []
        for stat in statistics:
            unit = stat.unit or ""
            stats_text.append(f"- {stat.name}: {stat.value}{unit}")

        return "\n".join(stats_text)

    def _build_prompt(self, description: str, word_count: int, statistics: List[Statistic]) -> str:
        """Build the prompt for text generation"""
        stats_formatted = self._format_statistics(statistics)

        prompt = f"""You are a professional document writer. Generate a comprehensive business document based on the following:

Description: {description}
Target Length: {word_count} words
Company Statistics:
{stats_formatted}

Requirements:
- Professional and formal tone
- Include sections: Executive Summary, Introduction, Main Content, Statistics Analysis, Conclusion
- Integrate the provided statistics naturally into the content
- Use clear headings and subheadings
- Ensure content is coherent and well-structured
- Write exactly around {word_count} words

Generate the document now:"""

        return prompt

    def generate_text(
        self,
        description: str,
        word_count: int,
        statistics: List[Statistic],
        max_retries: int = 1
    ) -> str:
        """
        Generate document text using Ollama local API

        Args:
            description: Document description/theme
            word_count: Target word count
            statistics: List of statistics to include
            max_retries: Maximum retry attempts

        Returns:
            Generated text content

        Raises:
            TextGenerationError: If text generation fails
        """
        try:
            logger.info(f"Starting text generation: word_count={word_count}, stats_count={len(statistics)}")
            logger.debug(f"Description: {description[:100]}...")

            prompt = self._build_prompt(description, word_count, statistics)
            logger.debug(f"Prompt length: {len(prompt)} characters")

            # Prepare payload based on API type
            if self.use_huggingface:
                # HuggingFace API payload
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": int(word_count * 2.0),
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "return_full_text": False
                    }
                }
            else:
                # Ollama API payload
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "num_predict": int(word_count * 2.0),
                    }
                }

            for attempt in range(max_retries):
                try:
                    logger.debug(f"Text generation attempt {attempt + 1}/{max_retries}")
                    logger.debug(f"Sending request to: {self.api_url}")

                    response = requests.post(
                        self.api_url,
                        json=payload,
                        headers=self.headers,
                        timeout=600  # 10 minutes timeout
                    )

                    logger.debug(f"Response status: {response.status_code}")

                    # Log response body for debugging 410 errors
                    if response.status_code == 410:
                        logger.error(f"HuggingFace returned 410 Gone")
                        logger.error(f"Response headers: {dict(response.headers)}")
                        logger.error(f"Response body: {response.text}")

                    response.raise_for_status()
                    result = response.json()

                    logger.debug(f"Response type: {type(result)}")

                    # Extract generated text based on API type
                    if self.use_huggingface:
                        # HuggingFace returns array with generated_text
                        if isinstance(result, list) and len(result) > 0:
                            generated_text = result[0].get("generated_text", "")
                        else:
                            generated_text = result.get("generated_text", "")
                    else:
                        # Ollama returns response in "response" field
                        generated_text = result.get("response", "")

                    # Clean up the text
                    generated_text = generated_text.strip()

                    if not generated_text:
                        logger.error("Empty response from text generation API")
                        raise TextGenerationError(
                            "Empty response from text generation API",
                            details={'attempt': attempt + 1, 'model': self.model}
                        )

                    actual_word_count = len(generated_text.split())
                    logger.info(f"Text generation successful: {actual_word_count} words generated (target: {word_count})")

                    return generated_text

                except requests.exceptions.Timeout:
                    logger.warning(f"Text generation timeout (attempt {attempt + 1}/{max_retries})")
                    if attempt == max_retries - 1:
                        raise TextGenerationError(
                            "Text generation timed out after multiple attempts",
                            details={'max_retries': max_retries, 'timeout': 600}
                        )
                    continue

                except requests.exceptions.RequestException as e:
                    logger.error(f"Request error during text generation: {str(e)}")
                    if attempt == max_retries - 1:
                        raise TextGenerationError(
                            f"Text generation request failed: {str(e)}",
                            details={'attempt': attempt + 1, 'model': self.model}
                        )
                    continue

            raise TextGenerationError(
                "Text generation failed after all retries",
                details={'max_retries': max_retries}
            )

        except TextGenerationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in text generation: {str(e)}", exc_info=True)
            raise TextGenerationError(
                f"Unexpected error in text generation: {str(e)}",
                details={'description': description[:50]}
            )

    def extract_title(self, text: str) -> str:
        """Extract a title from generated text"""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line) < 100:
                # Remove common markdown headers
                line = line.replace('#', '').strip()
                if line:
                    return line

        # Fallback to first sentence
        sentences = text.split('.')
        if sentences:
            return sentences[0][:100].strip()

        return "Generated Document"


text_generation_service = TextGenerationService()
