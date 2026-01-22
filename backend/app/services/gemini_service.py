"""
Gemini AI Service for text generation and content extraction
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for interacting with Google's Gemini AI"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini service with API key"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        # Use gemini-2.0-flash as the default model (fast and supports all features)
        self.model_name = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash")

        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            logger.warning("No valid Gemini API key found. Using fallback templates.")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                # Try to use the configured model, fall back to alternatives if needed
                try:
                    self.model = genai.GenerativeModel(self.model_name)
                    logger.info(f"Gemini service initialized with {self.model_name}")
                except Exception as init_error:
                    logger.debug(f"Failed to initialize with {self.model_name}: {init_error}")
                    # Try alternative models - using the correct model names with models/ prefix
                    for alt_model in ['models/gemini-2.0-flash', 'models/gemini-2.5-flash', 'models/gemini-flash-latest', 'models/gemini-2.0-flash-lite']:
                        try:
                            self.model = genai.GenerativeModel(alt_model)
                            logger.info(f"Gemini service initialized with fallback model {alt_model}")
                            self.model_name = alt_model  # Update the model name
                            break
                        except Exception as e:
                            logger.debug(f"Failed to initialize with {alt_model}: {e}")
                            continue

                    if not self.model:
                        # Last resort - use the fallback without AI
                        logger.warning("No compatible Gemini model found - using fallback mode")
                        self.model = None
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.model = None

    async def extract_invoice_data(self, user_prompt: str, document_type: str = "invoice") -> Dict[str, Any]:
        """Extract structured data from user prompt for invoice generation"""

        if not self.model:
            return self._get_fallback_invoice_data(user_prompt)

        system_prompt = """
        You are an AI assistant that extracts structured invoice data from user descriptions.

        Given a user's description, extract and generate appropriate invoice details.
        Return the data as a valid JSON object with the following structure:
        {
            "invoice_number": "string",
            "client_name": "string",
            "client_address": "string",
            "vendor_name": "string",
            "vendor_address": "string",
            "payment_terms": "string",
            "currency": "string (USD, EUR, etc.)",
            "notes": "string",
            "line_items": [
                {
                    "description": "string",
                    "quantity": number,
                    "unit_price": number,
                    "tax_rate": number (0-1)
                }
            ]
        }

        If information is not provided, generate reasonable defaults.
        For line items, create 2-5 items based on the context.
        Make the data realistic and professional.

        User prompt: """ + user_prompt + """

        Return ONLY the JSON object, no additional text or markdown.
        """

        try:
            response = self.model.generate_content(system_prompt)
            text = response.text.strip()

            # Clean up the response - remove markdown if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            # Parse JSON
            data = json.loads(text)

            # Ensure all required fields exist
            return self._validate_invoice_data(data)

        except Exception as e:
            logger.error(f"Gemini extraction failed: {e}")
            return self._get_fallback_invoice_data(user_prompt)

    async def generate_content(self, prompt: str, content_type: str = "general") -> str:
        """Generate text content based on prompt"""

        if not self.model:
            return self._get_fallback_content(prompt, content_type)

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return self._get_fallback_content(prompt, content_type)

    def _validate_invoice_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fill missing invoice data fields"""

        import random
        from datetime import datetime

        # Default values
        defaults = {
            "invoice_number": f"INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            "client_name": data.get("client_name", "Client Company LLC"),
            "client_address": data.get("client_address", "123 Business Ave\nNew York, NY 10001"),
            "vendor_name": data.get("vendor_name", "Professional Services Inc"),
            "vendor_address": data.get("vendor_address", "456 Commerce St\nSan Francisco, CA 94102"),
            "payment_terms": data.get("payment_terms", "Net 30 days"),
            "currency": data.get("currency", "USD"),
            "notes": data.get("notes", "Thank you for your business!"),
            "line_items": data.get("line_items", [])
        }

        # Ensure line items exist
        if not defaults["line_items"]:
            defaults["line_items"] = [
                {
                    "description": "Professional Services",
                    "quantity": 10,
                    "unit_price": 150.00,
                    "tax_rate": 0.0
                },
                {
                    "description": "Consultation Hours",
                    "quantity": 5,
                    "unit_price": 200.00,
                    "tax_rate": 0.0
                }
            ]

        # Validate line items
        for item in defaults["line_items"]:
            item["quantity"] = float(item.get("quantity", 1))
            item["unit_price"] = float(item.get("unit_price", 100))
            item["tax_rate"] = float(item.get("tax_rate", 0))

        return defaults

    def _get_fallback_invoice_data(self, user_prompt: str) -> Dict[str, Any]:
        """Generate fallback invoice data when Gemini is unavailable - with better parsing"""

        import random
        import re
        from datetime import datetime

        # Initialize default values
        invoice_data = {
            "invoice_number": f"INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            "client_name": "Client Company LLC",
            "client_address": "123 Business Ave\nNew York, NY 10001",
            "vendor_name": "Professional Services Inc",
            "vendor_address": "456 Commerce St\nSan Francisco, CA 94102",
            "payment_terms": "Net 30 days",
            "currency": "USD",
            "notes": "Thank you for your business!",
            "line_items": []
        }

        prompt_lower = user_prompt.lower()

        # Try to extract vendor information
        vendor_match = re.search(r'vendor:\s*([^,\.]+?)(?:,|\.|\n|$)', user_prompt, re.IGNORECASE)
        if vendor_match:
            vendor_info = vendor_match.group(1).strip()
            # Try to extract full vendor info including address
            vendor_full = re.search(r'vendor:\s*([^\.]+?)\.', user_prompt, re.IGNORECASE)
            if vendor_full:
                vendor_parts = vendor_full.group(1).split(',')
                if vendor_parts:
                    invoice_data["vendor_name"] = vendor_parts[0].strip()
                    if len(vendor_parts) > 1:
                        invoice_data["vendor_address"] = ', '.join(vendor_parts[1:]).strip()
            else:
                invoice_data["vendor_name"] = vendor_info

        # Try to extract customer/client information
        customer_match = re.search(r'(?:customer|client):\s*([^\.]+?)(?:\.|$)', user_prompt, re.IGNORECASE)
        if customer_match:
            customer_info = customer_match.group(1).strip()
            # Parse customer name and company
            if ' at ' in customer_info.lower():
                parts = customer_info.split(' at ', 1)
                invoice_data["client_name"] = parts[0].strip()
                if len(parts) > 1:
                    address_parts = parts[1].split(',')
                    if address_parts:
                        # First part might be company name + address
                        invoice_data["client_address"] = ', '.join(address_parts).strip()
            else:
                customer_parts = customer_info.split(',')
                if customer_parts:
                    invoice_data["client_name"] = customer_parts[0].strip()
                    if len(customer_parts) > 1:
                        invoice_data["client_address"] = ', '.join(customer_parts[1:]).strip()

        # Try to extract payment terms
        payment_match = re.search(r'payment terms?:\s*([^\.]+?)(?:\.|$)', user_prompt, re.IGNORECASE)
        if payment_match:
            invoice_data["payment_terms"] = payment_match.group(1).strip()

        # Try to extract tax rate
        tax_rate = 0
        tax_match = re.search(r'tax(?:\s+rate)?:\s*(\d+(?:\.\d+)?)\s*%', user_prompt, re.IGNORECASE)
        if tax_match:
            tax_rate = float(tax_match.group(1)) / 100

        # Try to extract notes
        notes_match = re.search(r'notes?:\s*([^\.]+?)(?:\.|$)', user_prompt, re.IGNORECASE)
        if notes_match:
            invoice_data["notes"] = notes_match.group(1).strip()

        # Try to detect currency
        if "eur" in prompt_lower or "euro" in prompt_lower or "€" in user_prompt:
            invoice_data["currency"] = "EUR"
        elif "gbp" in prompt_lower or "pound" in prompt_lower or "£" in user_prompt:
            invoice_data["currency"] = "GBP"

        # Try to extract line items
        items_match = re.search(r'items?:\s*([^\.]+?)(?:\.|payment|tax|notes|$)', user_prompt, re.IGNORECASE)
        if items_match:
            items_text = items_match.group(1)
            # Split by commas first to separate individual items
            item_parts = items_text.split(',')

            for part in item_parts:
                # Parse each item - look for pattern like "Item Name ($X x Y)" or "Item Name (X x Y)"
                item_pattern = r'([^(]+?)\s*\(\s*\$?([\d.]+)\s*x\s*(\d+)\s*\)'
                match = re.search(item_pattern, part)
                if match:
                    item_name, price, quantity = match.groups()
                    # Clean up item name - remove leading/trailing whitespace
                    clean_name = item_name.strip()
                    invoice_data["line_items"].append({
                        "description": clean_name,
                        "quantity": float(quantity),
                        "unit_price": float(price),
                        "tax_rate": tax_rate
                    })

            # Fallback to original regex if no items were found with comma splitting
            if not invoice_data["line_items"]:
                item_pattern = r'([^(]+?)\s*\(\s*\$?([\d.]+)\s*x\s*(\d+)\s*\)'
                items = re.findall(item_pattern, items_text)
                if items:
                    for item_name, price, quantity in items:
                        # Clean up item name - remove trailing commas and extra spaces
                        clean_name = item_name.strip().rstrip(',').strip()
                        invoice_data["line_items"].append({
                            "description": clean_name,
                            "quantity": float(quantity),
                            "unit_price": float(price),
                            "tax_rate": tax_rate
                        })

        # If no line items were extracted, check for common patterns
        if not invoice_data["line_items"]:
            if "jeans" in prompt_lower or "shirt" in prompt_lower or "dress" in prompt_lower:
                # Fashion items detected
                invoice_data["line_items"] = [
                    {"description": "Blue Denim Jeans", "quantity": 2, "unit_price": 45, "tax_rate": tax_rate},
                    {"description": "White Cotton T-Shirt", "quantity": 3, "unit_price": 25, "tax_rate": tax_rate},
                    {"description": "Black Leather Jacket", "quantity": 1, "unit_price": 120, "tax_rate": tax_rate},
                    {"description": "Red Summer Dress", "quantity": 2, "unit_price": 60, "tax_rate": tax_rate}
                ]
            elif "software" in prompt_lower or "development" in prompt_lower or "website" in prompt_lower:
                invoice_data["line_items"] = [
                    {"description": "Website Development", "quantity": 40, "unit_price": 150, "tax_rate": tax_rate},
                    {"description": "Mobile App Design", "quantity": 25, "unit_price": 125, "tax_rate": tax_rate},
                    {"description": "Database Optimization", "quantity": 10, "unit_price": 175, "tax_rate": tax_rate}
                ]
            else:
                # Default professional services
                invoice_data["line_items"] = [
                    {"description": "Professional Services", "quantity": 10, "unit_price": 150, "tax_rate": tax_rate},
                    {"description": "Consultation Hours", "quantity": 5, "unit_price": 200, "tax_rate": tax_rate}
                ]

        return invoice_data

    def validate_invoice_completeness(self, invoice_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate if invoice data has all required fields with meaningful values.
        Returns (is_complete, list_of_missing_fields)
        """
        missing_fields = []

        # Check required fields
        required_fields = {
            "client_name": "Customer/Client name",
            "vendor_name": "Vendor/Company name",
            "line_items": "Items or services to invoice"
        }

        for field, description in required_fields.items():
            if field not in invoice_data or not invoice_data[field]:
                missing_fields.append(description)
            elif field == "client_name" and invoice_data[field] in ["Client Company LLC", "Acme Corporation"]:
                missing_fields.append("Actual customer/client name (currently using placeholder)")
            elif field == "vendor_name" and invoice_data[field] in ["Professional Services Inc", "Tech Solutions LLC"]:
                missing_fields.append("Actual vendor/company name (currently using placeholder)")
            elif field == "line_items":
                if len(invoice_data[field]) == 0:
                    missing_fields.append(description)
                # Check if line items are just placeholders
                placeholder_items = ["Professional Services", "Consultation Hours", "Project Management", "Quality Assurance"]
                all_placeholders = all(
                    item.get("description", "") in placeholder_items
                    for item in invoice_data[field]
                )
                if all_placeholders and len(invoice_data[field]) > 1:
                    missing_fields.append("Specific items/services (currently using generic placeholders)")

        # Check optional but important fields
        if "client_address" in invoice_data and invoice_data["client_address"] in ["123 Business Ave\nNew York, NY 10001", "789 Enterprise Blvd\nChicago, IL 60601\nUSA"]:
            missing_fields.append("Actual client address (currently using placeholder)")

        is_complete = len(missing_fields) == 0
        return is_complete, missing_fields

    def _get_fallback_content(self, prompt: str, content_type: str) -> str:
        """Generate fallback content when Gemini is unavailable"""

        if content_type == "payment_terms":
            return "Payment is due within 30 days of invoice date. Late payments may incur a 2% monthly charge."
        elif content_type == "notes":
            return "Thank you for your business! We appreciate your continued partnership."
        else:
            return "Professional services delivered with excellence and attention to detail."