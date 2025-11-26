"""
Simple invoice data generator - extracts items, quantities, and prices from user description
"""
import json
import re
from typing import List, Dict
from app.services.text_generation import text_generation_service
from app.utils.logger import get_logger

logger = get_logger('simple_invoice_generator')


class SimpleInvoiceGeneratorService:
    """Service to extract invoice items from user description using AI"""

    def generate_invoice_items(self, description: str) -> List[Dict]:
        """
        Extract invoice items from user description

        Args:
            description: User's description containing items, quantities, and prices

        Returns:
            List of dictionaries with keys 'item', 'quantity', 'price'
        """
        logger.info("Extracting invoice items from description")
        logger.debug(f"Description: {description}")

        # Create prompt for AI to extract items
        prompt = self._create_extraction_prompt(description)

        try:
            # Generate invoice data using the text generation service
            if hasattr(text_generation_service, 'hf_client') and text_generation_service.hf_client:
                # Use HuggingFace InferenceClient with chat completions API
                response_obj = text_generation_service.hf_client.chat.completions.create(
                    model=text_generation_service.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3,  # Lower temperature for more accurate extraction
                    top_p=0.95
                )
                response = response_obj.choices[0].message.content
            else:
                # Fallback: use direct API call
                import requests
                if text_generation_service.use_huggingface:
                    # HuggingFace API
                    payload = {
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 1000,
                            "temperature": 0.3,
                            "top_p": 0.95,
                            "return_full_text": False
                        }
                    }
                    api_response = requests.post(
                        text_generation_service.api_url,
                        json=payload,
                        headers=text_generation_service.headers,
                        timeout=120
                    )
                    api_response.raise_for_status()
                    result = api_response.json()
                    response = result[0].get("generated_text", "") if isinstance(result, list) else result.get("generated_text", "")
                else:
                    # Ollama API
                    payload = {
                        "model": text_generation_service.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "top_p": 0.95,
                            "num_predict": 1000,
                        }
                    }
                    api_response = requests.post(
                        text_generation_service.api_url,
                        json=payload,
                        headers=text_generation_service.headers,
                        timeout=120
                    )
                    api_response.raise_for_status()
                    result = api_response.json()
                    response = result.get("response", "")

            logger.debug(f"AI response: {response}")

            # Extract JSON from response
            items = self._extract_json_from_response(response)
            logger.info(f"Successfully extracted {len(items)} items")

            return items

        except Exception as e:
            logger.error(f"Failed to extract invoice items: {str(e)}")
            # Fallback to basic extraction
            return self._fallback_extraction(description)

    def _create_extraction_prompt(self, description: str) -> str:
        """Create a prompt for AI to extract invoice items"""

        prompt = f"""Extract invoice line items from this description and return them as a JSON array.

Description: {description}

IMPORTANT INSTRUCTIONS:
1. Extract each item/service/product mentioned
2. Extract the quantity for each item (if not specified, use 1)
3. Extract the unit price for each item
4. If prices include "$", "USD", etc., extract just the numeric value
5. Return ONLY a JSON array, no other text

Example input: "2x Web Development $500 each, 3x Logo Design $150 each, 1x Hosting $50"
Example output:
[
  {{"item": "Web Development", "quantity": 2, "price": 500.00}},
  {{"item": "Logo Design", "quantity": 3, "price": 150.00}},
  {{"item": "Hosting", "quantity": 1, "price": 50.00}}
]

Now extract items from: {description}

Return ONLY the JSON array:"""

        return prompt

    def _extract_json_from_response(self, response: str) -> List[Dict]:
        """Extract JSON array from AI response"""
        # Remove markdown code blocks if present
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)

        # Find JSON array
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON array found in response")

        json_str = json_match.group(0)

        # Parse JSON
        try:
            items = json.loads(json_str)

            # Validate structure
            validated_items = []
            for item in items:
                if isinstance(item, dict) and 'item' in item and 'quantity' in item and 'price' in item:
                    validated_items.append({
                        'item': str(item['item']),
                        'quantity': float(item['quantity']),
                        'price': float(item['price'])
                    })

            if not validated_items:
                raise ValueError("No valid items found in JSON")

            return validated_items

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            logger.error(f"Attempted to parse: {json_str}")
            raise

    def _fallback_extraction(self, description: str) -> List[Dict]:
        """Fallback extraction using regex patterns"""
        logger.warning("Using fallback invoice item extraction")

        items = []

        # Pattern 1: "2x Item Name $100" or "2 x Item Name $100"
        pattern1 = r'(\d+)\s*x?\s*([^$]+?)\s*\$\s*([\d,]+\.?\d*)'
        matches1 = re.finditer(pattern1, description, re.IGNORECASE)

        for match in matches1:
            quantity = int(match.group(1))
            item_name = match.group(2).strip()
            price = float(match.group(3).replace(',', ''))
            items.append({
                'item': item_name,
                'quantity': quantity,
                'price': price
            })

        # Pattern 2: "Item Name: $100 (qty: 2)" or similar
        pattern2 = r'([^:$]+?):\s*\$\s*([\d,]+\.?\d*).*?(?:qty|quantity)[:\s]*(\d+)'
        matches2 = re.finditer(pattern2, description, re.IGNORECASE)

        for match in matches2:
            item_name = match.group(1).strip()
            price = float(match.group(2).replace(',', ''))
            quantity = int(match.group(3))
            items.append({
                'item': item_name,
                'quantity': quantity,
                'price': price
            })

        # If no items found, create a single generic item
        if not items:
            logger.warning("No items extracted, creating generic item")
            items.append({
                'item': 'Service/Product',
                'quantity': 1,
                'price': 100.00
            })

        logger.info(f"Fallback extraction found {len(items)} items")
        return items


# Singleton instance
simple_invoice_generator = SimpleInvoiceGeneratorService()
