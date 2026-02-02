"""
Gemini Text Generator Implementation.
Implements ITextGenerator interface using Google Gemini AI.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

from ...domain.interfaces.text_generator import ITextGenerator
from ...shared.logger import get_logger

logger = get_logger("gemini_text_generator")


class GeminiTextGenerator(ITextGenerator):
    """
    Gemini implementation of text generation.
    Uses Google Gemini AI for text generation with proper interface compliance.

    Features:
    - Structured output generation
    - Context-aware prompting
    - Comprehensive logging for model status
    - Fallback handling when API is unavailable
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "models/gemini-2.0-flash"
    ):
        """
        Initialize Gemini text generator.

        Args:
            api_key: Google AI API key (falls back to environment variable)
            model: Model identifier (default: gemini-2.0-flash)
        """
        self._api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self._model_name = model
        self._model = None
        self._is_active = False

        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize the Gemini model with comprehensive logging."""
        logger.info("=" * 60)
        logger.info("GEMINI TEXT GENERATOR INITIALIZATION")
        logger.info("=" * 60)

        if not GENAI_AVAILABLE:
            logger.warning("google-generativeai package not installed")
            logger.warning("Text generation will use fallback templates")
            logger.info("MODEL STATUS: INACTIVE (Package not installed)")
            logger.info("To enable: pip install google-generativeai")
            self._is_active = False
            return

        if not self._api_key or self._api_key == "your_gemini_api_key_here":
            logger.warning("No valid Gemini API key found")
            logger.warning("Text generation will use fallback templates")
            logger.info("MODEL STATUS: INACTIVE (No API Key)")
            self._is_active = False
            return

        try:
            genai.configure(api_key=self._api_key)
            logger.info(f"Attempting to initialize model: {self._model_name}")

            # Try primary model
            try:
                self._model = genai.GenerativeModel(self._model_name)
                logger.info(f"Successfully initialized: {self._model_name}")
                self._is_active = True
            except Exception as primary_error:
                logger.warning(f"Failed to initialize {self._model_name}: {primary_error}")

                # Try fallback models
                fallback_models = [
                    'models/gemini-2.0-flash',
                    'models/gemini-1.5-flash',
                    'models/gemini-flash-latest',
                    'models/gemini-2.0-flash-lite'
                ]

                for fallback in fallback_models:
                    if fallback == self._model_name:
                        continue
                    try:
                        self._model = genai.GenerativeModel(fallback)
                        self._model_name = fallback
                        logger.info(f"Successfully initialized fallback: {fallback}")
                        self._is_active = True
                        break
                    except Exception as fallback_error:
                        logger.debug(f"Fallback {fallback} failed: {fallback_error}")
                        continue

            if self._is_active:
                logger.info("MODEL STATUS: ACTIVE")
                logger.info(f"Provider: Google Gemini")
                logger.info(f"Model: {self._model_name}")
            else:
                logger.warning("MODEL STATUS: INACTIVE (All models failed)")

        except Exception as e:
            logger.error(f"Failed to configure Gemini: {e}")
            logger.info("MODEL STATUS: INACTIVE (Configuration Error)")
            self._is_active = False

        logger.info("=" * 60)

    @property
    def is_active(self) -> bool:
        """Check if the text generator is active and ready."""
        return self._is_active

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
        logger.info(f"Text generation requested - Model active: {self._is_active}")
        logger.debug(f"Prompt length: {len(prompt)} characters")

        if not self._is_active or not self._model:
            logger.warning("Model inactive, using fallback generation")
            return self._fallback_generation(prompt, context)

        try:
            # Build full prompt with context
            full_prompt = prompt
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                full_prompt = f"{context_str}\n\n{prompt}"

            # Configure generation settings
            generation_config = None
            if GENAI_AVAILABLE and genai:
                generation_config = genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )

            logger.info("Sending request to Gemini API...")
            response = self._model.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            result = response.text.strip()
            logger.info(f"Generation successful - Output length: {len(result)} characters")
            return result

        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            logger.warning("Falling back to template generation")
            return self._fallback_generation(prompt, context)

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
        logger.info(f"Structured generation requested - Model active: {self._is_active}")

        if not self._is_active or not self._model:
            logger.warning("Model inactive, returning default structure")
            return self._create_default_from_schema(output_schema)

        # Build structured prompt
        schema_prompt = f"""
{prompt}

You MUST respond with a valid JSON object matching this exact schema:
{json.dumps(output_schema, indent=2)}

IMPORTANT:
- Return ONLY the JSON object, no markdown formatting
- Do not wrap in code blocks
- Ensure all required fields are present
- Use appropriate data types as specified

Response (JSON only):
"""

        try:
            logger.info("Sending structured generation request...")
            generation_config = None
            if GENAI_AVAILABLE and genai:
                generation_config = genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.3  # Lower for structured output
                )
            response = self._model.generate_content(
                schema_prompt,
                generation_config=generation_config
            )

            text = response.text.strip()
            logger.debug(f"Raw response: {text[:200]}...")

            # Clean markdown if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            # Parse JSON
            result = json.loads(text)
            logger.info("Successfully parsed structured output")
            return result

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return self._create_default_from_schema(output_schema)
        except Exception as e:
            logger.error(f"Structured generation failed: {e}")
            return self._create_default_from_schema(output_schema)

    @property
    def model_name(self) -> str:
        """Return the model identifier."""
        return self._model_name

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "Google Gemini"

    def _fallback_generation(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Fallback generation when API is unavailable.

        Args:
            prompt: Original prompt
            context: Context information

        Returns:
            Template-based generated text
        """
        prompt_lower = prompt.lower()

        # Infographic-related prompts
        if "infographic" in prompt_lower or "section" in prompt_lower:
            return self._generate_infographic_fallback(prompt, context)

        # Invoice-related prompts
        if "payment" in prompt_lower and "terms" in prompt_lower:
            return ("Payment is due within 30 days of invoice date. "
                    "Late payments may incur a 2% monthly interest charge. "
                    "Please reference the invoice number when making payment.")

        if "terms" in prompt_lower and "conditions" in prompt_lower:
            return ("All services are provided as-is. Payment terms are net 30 days. "
                    "Disputes must be reported within 14 days of invoice date. "
                    "This invoice is subject to our standard terms of service.")

        # Default response
        return ("This content was generated using fallback templates. "
                "For full AI-generated content, please ensure the Gemini API key is configured.")

    def _generate_infographic_fallback(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate fallback content for infographic documents."""
        topic = "the subject matter"
        if context and "topic" in context:
            topic = context["topic"]

        return f"""Introduction to {topic.title()}

This section provides an overview of {topic}, examining its key aspects and significance
in the current landscape. Understanding these fundamentals is essential for comprehending
the broader implications and applications discussed throughout this document.

1. Background and Context

The development of {topic} has been marked by significant milestones and evolving
methodologies. Initial approaches laid the groundwork for current best practices,
while subsequent innovations have expanded the scope and applicability of core concepts.

   a. Historical Development
   The trajectory of {topic} reflects broader industry trends and technological
   advancements that have shaped modern approaches.

   b. Current State
   Present implementations demonstrate increased sophistication and integration
   with complementary systems and processes.

2. Key Considerations

Several factors warrant careful attention when examining {topic}:

   a. Primary factors include comprehensive assessment and strategic alignment
   b. Secondary considerations encompass resource allocation and timeline management
      i. Resource planning requires accurate estimation
      ii. Timeline management ensures appropriate sequencing

3. Implications and Applications

The practical applications of {topic} extend across multiple domains, offering
opportunities for improvement and innovation in various contexts.

This analysis provides a foundation for understanding {topic} and its relevance
to contemporary challenges and opportunities."""

    def _create_default_from_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create default values from a JSON schema.

        Args:
            schema: JSON schema

        Returns:
            Dictionary with default values
        """
        result = {}

        if "properties" in schema:
            for key, prop in schema["properties"].items():
                prop_type = prop.get("type", "string")

                if prop_type == "string":
                    result[key] = prop.get("default", "")
                elif prop_type == "number":
                    result[key] = prop.get("default", 0)
                elif prop_type == "integer":
                    result[key] = prop.get("default", 0)
                elif prop_type == "boolean":
                    result[key] = prop.get("default", False)
                elif prop_type == "array":
                    result[key] = prop.get("default", [])
                elif prop_type == "object":
                    result[key] = self._create_default_from_schema(prop)
                else:
                    result[key] = None

        return result

    def get_status_info(self) -> Dict[str, Any]:
        """
        Get detailed status information about the generator.

        Returns:
            Dictionary with status details
        """
        return {
            "provider": self.provider_name,
            "model": self.model_name,
            "is_active": self._is_active,
            "has_api_key": bool(self._api_key),
            "status": "ACTIVE" if self._is_active else "INACTIVE"
        }
