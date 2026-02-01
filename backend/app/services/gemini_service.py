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
        Tone: {tone}
        {sections_text}

        **CRITICAL WORD COUNT REQUIREMENT**:
        The document MUST be exactly {word_count} words (within +/- 50 words).
        This is a strict requirement - do NOT generate a shorter document.
        If {word_count} words seems long, expand each section with more detail, examples, analysis, and supporting arguments.
        Count your words and ensure you meet this requirement.

        FORMATTING RULES:
        1. DO NOT use bullet points (•, -, *) for any enumeration
        2. For lists and enumeration, use ONLY:
           - Numbers (1, 2, 3, etc.) for main points
           - Letters (a, b, c, etc.) for sub-points
           - Roman numerals (i, ii, iii, etc.) for sub-sub-points
        3. Use proper paragraph structure with clear topic sentences
        4. Include a comprehensive introduction and conclusion
        5. Use formal language appropriate for {tone} documents
        6. Do not use markdown formatting (no #, **, etc.)
        7. Use proper spacing between paragraphs

        STRUCTURE FOR A {word_count}-WORD DOCUMENT:
        - Introduction: ~{max(100, word_count // 10)} words
        - Main body sections: ~{word_count - (word_count // 5)} words total (divide among sections)
        - Conclusion: ~{max(100, word_count // 10)} words

        Each section should have multiple paragraphs with detailed explanations, examples, and analysis.
        Do not use filler content - make every sentence substantive and informative.

        Example of correct enumeration:
        1. First main point
           a. Sub-point under first main point
           b. Another sub-point
              i. Detail under sub-point
              ii. Another detail
        2. Second main point

        Generate professional, well-structured content that reads naturally and flows logically.
        Remember: The document MUST be {word_count} words. This is mandatory.
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

        # Get all available sections as (content, word_count) tuples
        all_sections = self._get_all_formal_sections(title, topic)

        # Select sections based on target word count
        selected_sections = []
        current_words = 0

        for content, words in all_sections:
            # Check if adding this section would go too far over target
            would_be_over = current_words + words - word_count
            # Add section if: under target, or if it wouldn't go too far over (150 word buffer)
            if current_words < word_count and would_be_over <= 150:
                selected_sections.append(content)
                current_words += words
            # Stop if we've reached or exceeded target
            if current_words >= word_count - 50:
                break

        # If still significantly under target, add appendices
        if current_words < word_count - 100:
            additional = self._generate_additional_content(topic, word_count - current_words + 50)
            selected_sections.append(additional)

        return "\n".join(selected_sections)

    def _get_all_formal_sections(self, title: str, topic: str) -> list:
        """Return all formal document sections as (content, word_count) tuples"""
        sections = []

        # Introduction (~120 words)
        intro = f"""{title}

Introduction

This document provides a comprehensive analysis and detailed examination of {topic}. The purpose of this document is to present a thorough overview of the subject matter, examining key aspects, relevant considerations, and actionable recommendations. The information presented herein has been compiled to support informed decision-making and strategic planning processes.

The scope of this analysis encompasses multiple dimensions of the topic, including historical context, current state assessment, future projections, and implementation guidance. Each section builds upon the previous to create a cohesive understanding of the subject matter and its implications for stakeholders.

Throughout this document, emphasis is placed on practical applications and real-world relevance. The analysis considers both immediate tactical concerns and longer-term strategic objectives, providing a balanced perspective that serves diverse stakeholder needs."""
        sections.append((intro, len(intro.split())))

        # Section 1: Background and Context (~350 words)
        section1 = f"""
1. Background and Context

The subject of {topic} has emerged as a critical area of focus in recent years, driven by evolving market dynamics, technological advancements, and shifting stakeholder expectations. Understanding the historical development and current positioning of this topic is essential for contextualizing subsequent analysis and recommendations.

   a. Historical Development and Evolution

   The trajectory of development in this area reflects broader industry trends and societal shifts. Initial recognition of the importance of this subject matter can be traced to foundational work that established core principles and frameworks. Subsequent phases of development have been characterized by refinement, expansion, and adaptation to changing circumstances.

   Key milestones in this evolution include the establishment of standardized practices, the emergence of specialized expertise, and the integration of technological solutions. Each phase has contributed to the current understanding and approach to the subject matter, building a foundation for continued advancement.

   The lessons learned from historical developments inform current best practices and guide future directions. Understanding this context enables more effective planning and decision-making, allowing stakeholders to build upon established foundations while avoiding previously identified pitfalls.

   b. Current State Assessment

   In the present context, this subject matter occupies a position of significant importance within the broader landscape. Current approaches reflect accumulated knowledge and experience, incorporating lessons learned and adapting to contemporary requirements.

   The present state is characterized by:
      i. Increased sophistication in analytical methods and frameworks
      ii. Greater integration with complementary disciplines and functions
      iii. Enhanced focus on measurable outcomes and accountability
      iv. Growing emphasis on stakeholder engagement and communication

   Assessment of the current state reveals both strengths to leverage and opportunities for improvement. The foundation established by previous efforts provides a solid base for continued development, while identified gaps present clear directions for enhancement.

   c. Relevance and Significance

   The significance of this topic extends across multiple dimensions, affecting various stakeholders and organizational functions. Recognition of this relevance is essential for securing appropriate attention and resources for related initiatives.

   Factors contributing to current relevance include:
      i. Changing regulatory and compliance requirements
      ii. Evolving best practices and industry standards
      iii. Increased stakeholder expectations and demands
      iv. Competitive pressures and market dynamics
      v. Technological capabilities and opportunities"""
        sections.append((section1, len(section1.split())))

        # Section 2: Analysis and Considerations (~400 words)
        section2 = f"""
2. Detailed Analysis and Key Considerations

A thorough analysis of {topic} requires examination of multiple factors and their interrelationships. This section presents a systematic review of critical elements, providing the analytical foundation for subsequent recommendations.

   a. Primary Strategic Factors

   The most critical elements requiring attention include comprehensive analytical assessment, meaningful stakeholder engagement, and strategic planning alignment. Each of these factors plays a vital role in determining outcomes and should receive appropriate prioritization.

   Comprehensive analytical assessment involves systematic evaluation of relevant data, trends, and indicators. This analysis should consider both quantitative metrics and qualitative factors, providing a balanced view of the current situation and future trajectory. Rigorous analysis enables informed decision-making and helps identify priorities for action.

   Meaningful stakeholder engagement ensures that diverse perspectives are considered and that those affected by decisions have appropriate input into the process. Effective engagement builds support for initiatives, identifies potential concerns early, and enhances the quality of outcomes through broader input.

   Strategic planning alignment ensures that efforts related to this topic support and advance broader organizational objectives. Alignment prevents duplication of effort, ensures efficient resource utilization, and maximizes the impact of investments in this area.

   b. Operational and Tactical Factors

   Supporting considerations at the operational level encompass resource allocation, timeline management, and quality assurance processes. These factors directly influence implementation success and should be carefully managed throughout the initiative lifecycle.

   Resource allocation decisions determine the capacity available for initiative execution. Appropriate resourcing requires accurate assessment of requirements, realistic estimation of costs, and alignment with available budgets. Under-resourcing leads to compromised outcomes, while over-resourcing diverts capacity from other priorities.

   Timeline management ensures that activities proceed according to plan and that dependencies are appropriately sequenced. Effective timeline management includes milestone identification, progress monitoring, and adjustment mechanisms for addressing variances from plan.

   Quality assurance processes ensure that deliverables meet established standards and that outcomes align with expectations. Quality considerations should be integrated throughout the initiative lifecycle, not addressed only at completion.

   c. Risk Assessment and Mitigation

   Effective management of {topic} requires identification and mitigation of associated risks. Risk assessment should consider both internal and external factors that could affect outcomes.

   Key risk categories include:
      i. Strategic risks related to alignment and direction
      ii. Operational risks affecting execution and delivery
      iii. Financial risks impacting resource availability
      iv. Reputational risks affecting stakeholder relationships
      v. Compliance risks related to regulatory requirements

   For each identified risk, appropriate mitigation strategies should be developed and implemented. Risk monitoring should continue throughout implementation, with adjustments made as circumstances evolve."""
        sections.append((section2, len(section2.split())))

        # Section 3: Recommendations (~450 words)
        section3 = f"""
3. Recommendations and Implementation Guidance

Based on the analysis presented in preceding sections, the following recommendations are proposed for addressing {topic}. These recommendations are organized by timeframe and priority to facilitate implementation planning.

   a. Immediate Actions (0-3 Months)

   Short-term actions focus on establishing foundations and addressing urgent priorities. These actions should be initiated promptly to build momentum and demonstrate commitment.

      i. Conduct Comprehensive Assessment
      Commission a detailed assessment of current state, identifying strengths, weaknesses, opportunities, and threats. This assessment should engage key stakeholders and leverage available data and expertise. Assessment findings will inform subsequent planning and prioritization.

      ii. Engage Key Stakeholders
      Initiate structured engagement with stakeholders to communicate intent, gather input, and build support. Stakeholder engagement should be ongoing throughout implementation, not a one-time activity. Early engagement helps identify concerns and builds coalition support.

      iii. Develop Implementation Framework
      Create a structured framework for implementation, including governance mechanisms, resource plans, and success metrics. The framework should provide clear guidance while allowing flexibility for adaptation as circumstances evolve.

      iv. Establish Quick Wins
      Identify and pursue opportunities for early successes that demonstrate value and build confidence. Quick wins generate momentum, validate approaches, and provide learning opportunities that inform subsequent efforts.

   b. Medium-Term Initiatives (3-12 Months)

   Medium-term initiatives build upon immediate actions and advance toward strategic objectives. These initiatives require sustained effort and resource commitment.

      i. Implement Core Capabilities
      Deploy foundational capabilities required for long-term success. Capability development should follow the established framework and incorporate lessons learned from initial activities.

      ii. Integrate with Existing Processes
      Ensure that new approaches integrate effectively with existing organizational processes and systems. Integration reduces friction, enhances adoption, and maximizes return on investment.

      iii. Develop Measurement Systems
      Establish robust measurement systems that track progress, evaluate outcomes, and inform continuous improvement. Measurement should address both leading indicators that predict future performance and lagging indicators that assess results.

      iv. Build Organizational Capability
      Invest in developing organizational capability through training, knowledge sharing, and skill development. Sustainable success requires broad organizational capability, not dependence on individual experts.

   c. Long-Term Strategy (12+ Months)

   Long-term strategic initiatives position the organization for sustained success and continued advancement in {topic}.

      i. Establish Monitoring and Adaptation Mechanisms
      Implement systems for ongoing monitoring of the environment and organizational performance. Monitoring enables early identification of emerging challenges and opportunities, supporting timely adaptation.

      ii. Plan for Continuous Improvement
      Embed continuous improvement principles into ongoing operations. Regular review cycles should assess performance, identify improvement opportunities, and implement enhancements.

      iii. Document and Share Lessons Learned
      Capture and disseminate lessons learned throughout implementation. Documentation supports organizational learning and helps avoid repetition of mistakes.

      iv. Evolve Strategy Based on Results
      Regularly review and update strategy based on implementation experience and changing circumstances. Strategy should be treated as a living document, subject to refinement as understanding deepens."""
        sections.append((section3, len(section3.split())))

        # Section 4: Conclusion (~200 words)
        section4 = f"""
4. Conclusion and Summary

This document has presented a comprehensive analysis of {topic}, examining background context, current state assessment, key considerations, and recommended actions. The analysis reveals both the significance of this subject matter and the opportunities available for improvement and advancement.

The recommendations provided offer a structured approach to addressing the challenges and opportunities identified. Implementation should proceed with careful attention to the factors discussed, maintaining focus on desired outcomes while remaining adaptable to changing circumstances.

Success in this area depends on sustained commitment, effective stakeholder collaboration, and adherence to established best practices. Leadership support, adequate resourcing, and clear accountability are essential enablers that must be maintained throughout implementation.

The path forward requires balancing ambition with pragmatism, pursuing meaningful improvements while managing risks and resource constraints. Progress should be measured against clear metrics, with regular review cycles enabling course correction as needed.

Continued attention to emerging developments in {topic} will be essential for maintaining relevance and effectiveness over time. The landscape continues to evolve, and approaches must evolve accordingly. Investment in ongoing learning and adaptation will position the organization for sustained success.

In conclusion, the subject matter addressed in this document merits continued attention and investment. The analysis and recommendations presented provide a foundation for action, while acknowledging that implementation will require ongoing effort and adaptation. With appropriate commitment and execution, the objectives outlined herein are achievable, delivering meaningful value to stakeholders and advancing organizational objectives."""
        sections.append((section4, len(section4.split())))

        return sections

    def _generate_additional_content(self, topic: str, words_needed: int) -> str:
        """Generate additional content paragraphs to meet word count target"""
        additional_paragraphs = []

        # Generate enough paragraphs to meet the word count
        paragraph_templates = [
            f"""

Appendix A: Detailed Implementation Considerations

The implementation of initiatives related to {topic} requires attention to numerous practical considerations that influence success. This appendix provides additional detail on key implementation factors.

Resource planning must account for both direct costs and indirect investments required for success. Direct costs include personnel time, technology investments, and external expertise. Indirect investments include opportunity costs, training requirements, and organizational change management efforts. Comprehensive resource planning prevents mid-implementation surprises that can derail progress.

Change management considerations are particularly important given the organizational impact of initiatives in this area. Effective change management addresses the human dimensions of change, including communication, training, and support systems. Resistance to change is natural and should be anticipated and addressed proactively.

Technology considerations may include both enabling systems and integration requirements. Technology decisions should be driven by business requirements rather than technical preferences. Integration with existing systems is often more challenging and important than new system implementation.""",

            f"""

Appendix B: Stakeholder Analysis and Engagement Strategy

Effective stakeholder engagement requires systematic analysis of stakeholder interests, influence, and engagement preferences. This appendix outlines key considerations for stakeholder management.

Stakeholder identification should be comprehensive, considering all parties who may be affected by or who may influence initiatives related to {topic}. Stakeholders may include internal parties such as leadership, management, and staff, as well as external parties including customers, partners, regulators, and communities.

For each stakeholder group, analysis should assess their interests in the initiative, their potential influence on outcomes, and their current disposition toward proposed changes. This analysis informs engagement strategy, helping prioritize effort and tailor approaches to different stakeholder needs.

Engagement approaches should be matched to stakeholder characteristics and requirements. Some stakeholders require detailed information and involvement in decision-making, while others need only periodic updates. Resource-efficient engagement focuses effort where it will have the greatest impact.""",

            f"""

Appendix C: Performance Metrics and Evaluation Framework

Measurement of progress and outcomes is essential for effective management of {topic}. This appendix outlines a framework for performance measurement and evaluation.

Key performance indicators should address multiple dimensions of performance, including implementation progress, operational outcomes, and strategic impact. Balanced measurement prevents overemphasis on any single dimension and provides comprehensive visibility into initiative health.

Leading indicators predict future performance and enable proactive management. Examples include stakeholder sentiment, resource utilization, and milestone completion rates. Monitoring leading indicators enables early intervention when performance diverges from expectations.

Lagging indicators assess actual outcomes and results. Examples include objective achievement, benefit realization, and stakeholder satisfaction. Lagging indicators validate that activities are producing intended results and inform future planning.

Regular reporting should communicate performance to relevant stakeholders, supporting transparency and accountability. Reports should be tailored to audience needs, with executive summaries for leadership and detailed analyses for operational management.""",

            f"""

Appendix D: Risk Register and Mitigation Plans

Comprehensive risk management requires systematic identification, assessment, and mitigation of potential risks. This appendix documents key risks and associated mitigation strategies.

Strategic risks relate to overall direction and alignment of initiatives with organizational objectives. Mitigation strategies include regular strategy review, stakeholder alignment processes, and clear governance mechanisms. Strategic risks often have the highest potential impact but may be difficult to detect early.

Operational risks affect day-to-day execution and delivery of initiatives. Mitigation strategies include robust planning, adequate resourcing, and effective project management practices. Operational risks are often more predictable and manageable than strategic risks.

External risks arise from factors outside organizational control, including market conditions, regulatory changes, and competitive actions. Mitigation strategies include environmental scanning, scenario planning, and building adaptive capacity. External risks require ongoing monitoring and flexible response capabilities.""",

            f"""

Appendix E: Implementation Timeline and Milestones

Successful implementation of {topic} requires careful timeline planning with clearly defined milestones. This appendix outlines a comprehensive implementation schedule designed to ensure systematic progress toward objectives.

Phase 1 activities, spanning the initial one to three months, focus on foundation building and preparation. Key milestones include completion of initial assessment, stakeholder mapping and engagement planning, resource allocation and team formation, and governance structure establishment. These foundational activities set the stage for subsequent implementation phases.

Phase 2 activities, spanning months four through nine, focus on core implementation and capability building. Key milestones include deployment of primary capabilities, integration with existing systems and processes, initial outcome measurement and reporting, and adjustment based on early learnings. This phase represents the bulk of implementation effort and investment.

Phase 3 activities, spanning months ten through twelve and beyond, focus on optimization and sustainability. Key milestones include full operational capability achievement, performance optimization based on experience, transition to ongoing operations, and documentation of lessons learned for future reference.""",

            f"""

Appendix F: Communication Strategy and Plan

Effective communication is essential for success in {topic}. This appendix outlines the communication strategy and specific communication activities planned throughout implementation.

Communication objectives include building awareness and understanding of the initiative, engaging stakeholders in meaningful dialogue, providing transparency regarding progress and challenges, and celebrating successes and recognizing contributions. Each objective requires specific communication activities and channels.

Target audiences for communication include executive leadership requiring strategic updates and decision support, operational management requiring detailed progress information, staff requiring understanding of impacts and expectations, and external stakeholders requiring appropriate information about organizational activities.

Communication channels should be selected based on message content and audience preferences. Formal channels include reports, presentations, and official announcements. Informal channels include conversations, team meetings, and collaborative platforms. Multi-channel approaches ensure messages reach intended audiences effectively.""",

            f"""

Appendix G: Resource Requirements and Budget Considerations

Implementation of {topic} requires adequate resources allocated appropriately across the initiative lifecycle. This appendix provides detailed resource requirements and budget considerations.

Personnel resources include dedicated team members responsible for implementation activities, subject matter experts providing specialized knowledge and guidance, and leadership sponsors providing direction and organizational support. Resource loading should account for both full-time dedication and part-time contributions.

Financial resources include direct costs such as technology, consulting services, and training, as well as indirect costs such as personnel time and opportunity costs. Budget planning should include appropriate contingency for unexpected requirements.

Technology resources may include new systems acquisition, existing system modifications, integration development, and ongoing operational support. Technology decisions should be driven by business requirements with appropriate technical input.

External resources such as consultants, vendors, and partners may supplement internal capabilities. External resource engagement should be managed to ensure knowledge transfer and avoid excessive dependency."""
        ]

        # Add paragraphs until we approach the target
        words_added = 0
        for paragraph in paragraph_templates:
            if words_added >= words_needed:
                break
            additional_paragraphs.append(paragraph)
            words_added += len(paragraph.split())

        return "\n".join(additional_paragraphs)

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