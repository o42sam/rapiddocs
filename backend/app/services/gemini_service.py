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

    async def extract_formal_document_data(self, user_prompt: str) -> Dict[str, Any]:
        """
        Extract structured data from user prompt for formal document generation.
        Extracts: title, topic, word count, tone, sections, etc.
        """
        if not self.model:
            return self._get_fallback_formal_data(user_prompt)

        system_prompt = """
        You are an AI assistant that extracts structured data from user descriptions for formal document generation.

        Given a user's description, extract document parameters and return as a valid JSON object:
        {
            "title": "string - document title",
            "topic": "string - main topic/subject",
            "word_count": number (target word count, default 500 if not specified),
            "tone": "string - one of: professional, academic, legal, business, formal (default: professional)",
            "sections": ["list of section titles/topics to cover"],
            "author": "string - author/organization name if mentioned",
            "date": "string - date if mentioned, else current date",
            "summary": "string - brief 1-2 sentence summary of what the document should cover"
        }

        Parse carefully:
        - If user mentions "X words" or "approximately X words", extract that as word_count
        - If user mentions "brief" or "short", use word_count of 300-500
        - If user mentions "detailed" or "comprehensive", use word_count of 1000-2000
        - If user mentions "report", "analysis", "whitepaper", default to professional/business tone
        - If user mentions "legal", "contract", "agreement", use legal tone
        - If user mentions "academic", "research", "thesis", use academic tone

        User prompt: """ + user_prompt + """

        Return ONLY the JSON object, no additional text or markdown.
        """

        try:
            response = self.model.generate_content(system_prompt)
            text = response.text.strip()

            # Clean up markdown if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            data = json.loads(text)
            return self._validate_formal_data(data, user_prompt)

        except Exception as e:
            logger.error(f"Gemini formal data extraction failed: {e}")
            return self._get_fallback_formal_data(user_prompt)

    async def generate_formal_document_content(self, document_data: Dict[str, Any]) -> str:
        """
        Generate the full text content for a formal document.
        Uses numbers, letters, and roman numerals for enumeration (NO bullet points).
        """
        title = document_data.get("title", "Formal Document")
        topic = document_data.get("topic", document_data.get("summary", ""))
        word_count = document_data.get("word_count", 500)
        tone = document_data.get("tone", "professional")
        sections = document_data.get("sections", [])

        if not self.model:
            return self._get_fallback_formal_content(document_data)

        sections_text = ""
        if sections:
            sections_text = f"\nCover these sections/topics: {', '.join(sections)}"

        system_prompt = f"""
        Generate a formal document with the following specifications:

        Title: {title}
        Topic/Subject: {topic}
        Target word count: approximately {word_count} words
        Tone: {tone}
        {sections_text}

        IMPORTANT FORMATTING RULES:
        1. DO NOT use bullet points (•, -, *) for any enumeration
        2. For lists and enumeration, use ONLY:
           - Numbers (1, 2, 3, etc.) for main points
           - Letters (a, b, c, etc.) for sub-points
           - Roman numerals (i, ii, iii, etc.) for sub-sub-points
        3. Use proper paragraph structure with clear topic sentences
        4. Include an introduction and conclusion
        5. Use formal language appropriate for {tone} documents
        6. Do not use markdown formatting (no #, **, etc.)
        7. Use proper spacing between paragraphs

        Example of correct enumeration:
        1. First main point
           a. Sub-point under first main point
           b. Another sub-point
              i. Detail under sub-point
              ii. Another detail
        2. Second main point

        Generate professional, well-structured content that reads naturally and flows logically.
        The document should be substantive and informative, not generic filler text.
        """

        try:
            response = self.model.generate_content(system_prompt)
            content = response.text.strip()

            # Clean up any markdown that might have slipped through
            content = self._clean_formal_content(content)

            return content

        except Exception as e:
            logger.error(f"Gemini formal content generation failed: {e}")
            return self._get_fallback_formal_content(document_data)

    def _validate_formal_data(self, data: Dict[str, Any], original_prompt: str) -> Dict[str, Any]:
        """Validate and fill missing formal document data fields"""
        import re
        from datetime import datetime

        # Extract word count from original prompt if not in data
        word_count = data.get("word_count", 500)
        word_match = re.search(r'(\d+)\s*words?', original_prompt.lower())
        if word_match:
            word_count = int(word_match.group(1))

        # Validate word count bounds
        word_count = max(100, min(word_count, 10000))

        defaults = {
            "title": data.get("title", "Formal Document"),
            "topic": data.get("topic", original_prompt[:200] if len(original_prompt) > 200 else original_prompt),
            "word_count": word_count,
            "tone": data.get("tone", "professional"),
            "sections": data.get("sections", []),
            "author": data.get("author", ""),
            "date": data.get("date", datetime.now().strftime("%B %d, %Y")),
            "summary": data.get("summary", original_prompt[:300] if len(original_prompt) > 300 else original_prompt)
        }

        # Validate tone
        valid_tones = ["professional", "academic", "legal", "business", "formal"]
        if defaults["tone"].lower() not in valid_tones:
            defaults["tone"] = "professional"

        return defaults

    def _get_fallback_formal_data(self, user_prompt: str) -> Dict[str, Any]:
        """Generate fallback formal document data when Gemini is unavailable"""
        import re
        from datetime import datetime

        # Try to extract word count
        word_count = 500
        word_match = re.search(r'(\d+)\s*words?', user_prompt.lower())
        if word_match:
            word_count = int(word_match.group(1))
        elif "brief" in user_prompt.lower() or "short" in user_prompt.lower():
            word_count = 300
        elif "detailed" in user_prompt.lower() or "comprehensive" in user_prompt.lower():
            word_count = 1500

        # Determine tone from keywords
        tone = "professional"
        if any(word in user_prompt.lower() for word in ["legal", "contract", "agreement", "terms"]):
            tone = "legal"
        elif any(word in user_prompt.lower() for word in ["academic", "research", "thesis", "study"]):
            tone = "academic"
        elif any(word in user_prompt.lower() for word in ["business", "corporate", "company"]):
            tone = "business"

        # Try to extract a title
        title = "Formal Document"
        title_patterns = [
            r'(?:titled?|about|regarding|on)\s+["\']?([^"\'\.]+)["\']?',
            r'^([A-Z][^\.]{10,50})',
        ]
        for pattern in title_patterns:
            match = re.search(pattern, user_prompt, re.IGNORECASE)
            if match:
                title = match.group(1).strip()[:100]
                break

        return {
            "title": title,
            "topic": user_prompt[:200] if len(user_prompt) > 200 else user_prompt,
            "word_count": word_count,
            "tone": tone,
            "sections": [],
            "author": "",
            "date": datetime.now().strftime("%B %d, %Y"),
            "summary": user_prompt[:300] if len(user_prompt) > 300 else user_prompt
        }

    def _get_fallback_formal_content(self, document_data: Dict[str, Any]) -> str:
        """Generate fallback formal document content when Gemini is unavailable"""
        title = document_data.get("title", "Document")
        topic = document_data.get("topic", "")
        word_count = document_data.get("word_count", 500)
        tone = document_data.get("tone", "professional")

        # Generate a structured fallback document
        content = f"""{title}

Introduction

This document provides a comprehensive overview of {topic}. The following sections outline the key aspects, considerations, and recommendations relevant to this subject matter.

1. Background and Context

The subject of {topic} has gained significant attention in recent years. Understanding the fundamental aspects is essential for proper assessment and decision-making.

   a. Historical Development
   The evolution of this topic reflects broader trends in the field. Key milestones include initial recognition of the importance, subsequent research and development, and current state-of-the-art practices.

   b. Current Relevance
   In today's context, this subject matter holds particular significance due to:
      i. Changing regulatory requirements
      ii. Evolving best practices
      iii. Increased stakeholder expectations

2. Key Considerations

Several factors merit careful attention when addressing this topic:

   a. Primary Factors
   The most critical elements include thorough analysis, stakeholder engagement, and strategic planning.

   b. Secondary Factors
   Supporting considerations encompass resource allocation, timeline management, and quality assurance.

3. Recommendations

Based on the analysis presented, the following recommendations are proposed:

   a. Short-term Actions
      i. Conduct comprehensive assessment
      ii. Engage relevant stakeholders
      iii. Develop implementation framework

   b. Long-term Strategy
      i. Establish monitoring mechanisms
      ii. Plan for continuous improvement
      iii. Document lessons learned

4. Conclusion

This document has outlined the essential aspects of {topic}. The recommendations provided offer a structured approach to addressing the relevant challenges and opportunities. Implementation should proceed with careful attention to the factors identified herein.

The success of any initiative in this area depends on commitment to excellence, stakeholder collaboration, and adherence to established best practices. Continued attention to emerging developments will ensure sustained relevance and effectiveness.
"""
        return content

    def _clean_formal_content(self, content: str) -> str:
        """Clean up formal document content - remove markdown and bullet points"""
        import re

        # Remove markdown headers
        content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)

        # Remove bold/italic markdown
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
        content = re.sub(r'\*([^*]+)\*', r'\1', content)
        content = re.sub(r'__([^_]+)__', r'\1', content)
        content = re.sub(r'_([^_]+)_', r'\1', content)

        # Replace bullet points with numbered lists where possible
        # This is a simple conversion - lines starting with - or * or •
        lines = content.split('\n')
        result_lines = []
        list_counter = 1

        for line in lines:
            stripped = line.lstrip()
            indent = len(line) - len(stripped)

            # Check for bullet points
            if stripped.startswith(('- ', '* ', '• ')):
                # Replace with number
                new_line = ' ' * indent + f"{list_counter}. " + stripped[2:]
                result_lines.append(new_line)
                list_counter += 1
            else:
                result_lines.append(line)
                # Reset counter on non-list lines
                if stripped and not stripped[0].isdigit():
                    list_counter = 1

        return '\n'.join(result_lines)