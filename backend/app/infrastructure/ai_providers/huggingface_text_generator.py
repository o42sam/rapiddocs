"""
HuggingFace Text Generator Implementation.
Uses HuggingFace API for text generation.
"""

from typing import Dict, Any, Optional
import logging
import json
import aiohttp
from ...domain.interfaces.text_generator import ITextGenerator

logger = logging.getLogger(__name__)


class HuggingFaceTextGenerator(ITextGenerator):
    """
    HuggingFace implementation of text generation.
    Uses HuggingFace Inference API for various models.
    """

    def __init__(self, api_key: str, model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"):
        """
        Initialize HuggingFace text generator.

        Args:
            api_key: HuggingFace API key
            model: Model identifier on HuggingFace
        """
        self._api_key = api_key
        self._model = model
        self._api_url = f"https://api-inference.huggingface.co/models/{model}"
        self._headers = {"Authorization": f"Bearer {api_key}"}

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
        try:
            # Prepare the request payload
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": min(max_tokens, 1000),  # HF has limits
                    "temperature": temperature,
                    "do_sample": temperature > 0,
                    "top_p": 0.95,
                    "return_full_text": False
                }
            }

            # Add context to prompt if provided
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                payload["inputs"] = f"{context_str}\n\n{prompt}"

            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self._api_url,
                    headers=self._headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Extract generated text
                        if isinstance(result, list) and len(result) > 0:
                            return result[0].get("generated_text", "")
                        return ""
                    else:
                        error_text = await response.text()
                        logger.error(f"HuggingFace API error: {response.status} - {error_text}")

                        # Fallback to simple template-based generation
                        return self._fallback_generation(prompt, context)

        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            # Use fallback generation
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
        # Add schema instruction to prompt
        schema_prompt = f"""
        {prompt}

        Please provide the response in the following JSON format:
        {json.dumps(output_schema, indent=2)}

        Response (JSON only):
        """

        # Generate text
        generated = await self.generate(
            prompt=schema_prompt,
            max_tokens=max_tokens,
            temperature=0.3  # Lower temperature for structured output
        )

        # Try to parse JSON from response
        try:
            # Find JSON in the response
            json_start = generated.find('{')
            json_end = generated.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = generated[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"Failed to parse structured output: {e}")

        # Return default structure based on schema
        return self._create_default_from_schema(output_schema)

    @property
    def model_name(self) -> str:
        """Return the model identifier."""
        return self._model

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "HuggingFace"

    def _fallback_generation(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        """
        Fallback generation when API fails.
        Uses template-based generation for common prompts.

        Args:
            prompt: Original prompt
            context: Context information

        Returns:
            Generated text based on templates
        """
        prompt_lower = prompt.lower()

        # Invoice-related prompts
        if "payment" in prompt_lower and "terms" in prompt_lower:
            return "Payment is due within 30 days of invoice date. Late payments may incur a 2% monthly interest charge. Please reference the invoice number when making payment."

        elif "terms" in prompt_lower and "conditions" in prompt_lower:
            return "All services are provided as-is. Payment terms are net 30 days. Disputes must be reported within 14 days of invoice date. This invoice is subject to our standard terms of service."

        elif "invoice" in prompt_lower and "note" in prompt_lower:
            return "Thank you for your business! We appreciate your continued partnership. For any questions regarding this invoice, please don't hesitate to contact our billing department."

        elif "line item" in prompt_lower or "invoice item" in prompt_lower:
            return """Professional Services - Consultation and Analysis
Technical Implementation - Development and Deployment
Quality Assurance - Testing and Validation
Project Management - Coordination and Reporting
Documentation - Technical and User Documentation"""

        # Default response
        return "Thank you for your business. Please contact us if you have any questions or concerns regarding this document."

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