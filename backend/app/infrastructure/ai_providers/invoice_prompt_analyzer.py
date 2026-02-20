"""
Invoice Prompt Analyzer for Invoice Document Generation.
Extracts structured invoice data from user prompts using Gemini AI.
Always runs regex extraction as a baseline, then enhances with AI results.
"""

import re
import json
import random
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

from .gemini_text_generator import GeminiTextGenerator
from ...shared.logger import get_logger

logger = get_logger("invoice_prompt_analyzer")


PLACEHOLDER_VENDORS = {"Professional Services Inc", ""}
PLACEHOLDER_CLIENTS = {"Client Company LLC", ""}


@dataclass
class InvoiceLineItemExtraction:
    """Extracted line item from user prompt."""
    description: str
    quantity: float
    unit_price: float
    tax_rate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "description": self.description,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "tax_rate": self.tax_rate
        }


@dataclass
class InvoiceExtractionResult:
    """Result of extracting invoice data from user prompt."""
    invoice_number: str
    client_name: str
    client_address: str
    vendor_name: str
    vendor_address: str
    currency: str
    payment_terms: str
    notes: str
    line_items: List[InvoiceLineItemExtraction]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "invoice_number": self.invoice_number,
            "client_name": self.client_name,
            "client_address": self.client_address,
            "vendor_name": self.vendor_name,
            "vendor_address": self.vendor_address,
            "currency": self.currency,
            "payment_terms": self.payment_terms,
            "notes": self.notes,
            "line_items": [item.to_dict() for item in self.line_items]
        }


class InvoicePromptAnalyzer:
    """
    Analyzes user prompts to extract structured data for invoice generation.
    Uses Gemini AI for intelligent extraction with regex as baseline/fallback.

    Strategy:
    1. Always run regex extraction first (fast, reliable for structured prompts)
    2. If AI is available, also run AI extraction
    3. Merge: prefer AI values where non-empty, fill gaps with regex results
    """

    EXTRACTION_SCHEMA = {
        "type": "object",
        "properties": {
            "invoice_number": {"type": "string", "description": "Invoice number (e.g. INV-2024-001)"},
            "client_name": {"type": "string", "description": "Client/customer company or person name"},
            "client_address": {"type": "string", "description": "Client address"},
            "vendor_name": {"type": "string", "description": "Vendor/company name"},
            "vendor_address": {"type": "string", "description": "Vendor address"},
            "currency": {"type": "string", "description": "Currency code (USD, EUR, GBP, etc.)"},
            "payment_terms": {"type": "string", "description": "Payment terms"},
            "notes": {"type": "string", "description": "Invoice notes"},
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "number"},
                        "unit_price": {"type": "number"},
                        "tax_rate": {"type": "number", "description": "Tax rate as decimal (0-1)"}
                    }
                }
            }
        }
    }

    def __init__(self, text_generator: GeminiTextGenerator):
        """
        Initialize the invoice prompt analyzer.

        Args:
            text_generator: Gemini text generator for AI-powered extraction
        """
        self._text_generator = text_generator
        logger.info("Invoice Prompt Analyzer initialized")
        logger.info(f"Using text generator: {text_generator.provider_name} - {text_generator.model_name}")
        logger.info(f"Text generator active: {text_generator.is_active}")

    async def analyze(self, user_prompt: str) -> InvoiceExtractionResult:
        """
        Analyze a user prompt and extract structured invoice data.

        Strategy: always run regex first as a baseline, then try AI to enhance.
        This ensures we never lose data when the AI model returns empty results.

        Args:
            user_prompt: The user's description/prompt for the invoice

        Returns:
            InvoiceExtractionResult with extracted data
        """
        logger.info("=" * 50)
        logger.info("INVOICE PROMPT ANALYSIS STARTED")
        logger.info("=" * 50)
        logger.info(f"Input prompt length: {len(user_prompt)} characters")

        # Step 1: Always run regex extraction as a reliable baseline
        regex_result = self._regex_extraction(user_prompt)
        logger.info(f"Regex extracted: vendor='{regex_result.vendor_name}', client='{regex_result.client_name}', items={len(regex_result.line_items)}")

        # Step 2: If AI is available, try AI extraction and merge
        if self._text_generator.is_active:
            logger.info("AI model active - running AI extraction")
            ai_result = await self._ai_extraction(user_prompt)
            logger.info(f"AI extracted: vendor='{ai_result.vendor_name}', client='{ai_result.client_name}', items={len(ai_result.line_items)}")
            result = self._merge_results(ai_result, regex_result)
            logger.info("Merged AI + regex results")
        else:
            logger.info("AI model inactive - using regex results only")
            result = regex_result

        # Step 3: Fill remaining gaps with defaults
        result = self._fill_defaults(result)

        logger.info("FINAL EXTRACTION RESULTS:")
        logger.info(f"  Vendor: {result.vendor_name}")
        logger.info(f"  Vendor Address: {result.vendor_address[:50]}...")
        logger.info(f"  Client: {result.client_name}")
        logger.info(f"  Client Address: {result.client_address[:50]}...")
        logger.info(f"  Currency: {result.currency}")
        logger.info(f"  Line Items: {len(result.line_items)}")
        for item in result.line_items:
            logger.info(f"    - {item.description}: qty={item.quantity}, price={item.unit_price}, tax={item.tax_rate}")
        logger.info("=" * 50)

        return result

    def _merge_results(
        self,
        ai_result: InvoiceExtractionResult,
        regex_result: InvoiceExtractionResult
    ) -> InvoiceExtractionResult:
        """
        Merge AI and regex results, preferring AI values where non-empty/non-placeholder.

        Args:
            ai_result: Result from AI extraction
            regex_result: Result from regex extraction

        Returns:
            Merged InvoiceExtractionResult
        """
        def pick_best(ai_val: str, regex_val: str, placeholders: set) -> str:
            """Pick AI value if it's real data, otherwise regex value."""
            if ai_val and ai_val not in placeholders:
                return ai_val
            if regex_val and regex_val not in placeholders:
                return regex_val
            return ai_val or regex_val

        # Prefer AI line items if they exist, otherwise regex
        ai_has_real_items = (
            len(ai_result.line_items) > 0
            and not all(
                item.description in {"Professional Services", "Consultation Hours", "Service", ""}
                for item in ai_result.line_items
            )
        )
        line_items = ai_result.line_items if ai_has_real_items else regex_result.line_items

        return InvoiceExtractionResult(
            invoice_number=ai_result.invoice_number or regex_result.invoice_number,
            vendor_name=pick_best(ai_result.vendor_name, regex_result.vendor_name, PLACEHOLDER_VENDORS),
            vendor_address=pick_best(ai_result.vendor_address, regex_result.vendor_address, {"456 Commerce St\nSan Francisco, CA 94102", ""}),
            client_name=pick_best(ai_result.client_name, regex_result.client_name, PLACEHOLDER_CLIENTS),
            client_address=pick_best(ai_result.client_address, regex_result.client_address, {"123 Business Ave\nNew York, NY 10001", ""}),
            currency=ai_result.currency or regex_result.currency or "USD",
            payment_terms=ai_result.payment_terms or regex_result.payment_terms or "Net 30 days",
            notes=ai_result.notes or regex_result.notes or "Thank you for your business!",
            line_items=line_items
        )

    async def _ai_extraction(self, user_prompt: str) -> InvoiceExtractionResult:
        """
        Extract invoice data using AI.

        Args:
            user_prompt: User's prompt

        Returns:
            Extracted invoice data (may have empty fields if AI fails)
        """
        extraction_prompt = f"""
You are an expert invoice data extractor. Analyze the following user prompt and extract
structured invoice information.

USER PROMPT:
{user_prompt}

Extract the following information:

1. invoice_number: An invoice number if mentioned, otherwise generate one like "INV-YYYYMMDD-XXXX"
2. client_name: The client/customer/recipient name or company (who the invoice is TO)
3. client_address: The client's address if mentioned
4. vendor_name: The vendor/company/sender name (who the invoice is FROM)
5. vendor_address: The vendor's address if mentioned
6. currency: Currency code (USD, EUR, GBP, etc.) - detect from symbols ($, EUR, etc.) or default to USD
7. payment_terms: Payment terms if mentioned, otherwise "Net 30 days"
8. notes: Any notes mentioned, otherwise "Thank you for your business!"
9. line_items: Array of items/services, each with:
   - description: What the item/service is
   - quantity: How many (default 1)
   - unit_price: Price per unit
   - tax_rate: Tax rate as decimal 0-1 (default 0)

IMPORTANT parsing rules:
- "Vendor: X" or "from X" means X is the vendor name
- "Customer: X" or "Client: X" or "to X" means X is the client name
- "Customer: Person at Company, Address" means the client_name is "Person at Company" and client_address is the address
- "X hours of consulting at $Y/hour" means quantity=X, unit_price=Y
- "X units of Y at $Z each" means quantity=X, description=Y, unit_price=Z
- "Item ($X x Y)" means description=Item, unit_price=X, quantity=Y
- If amounts use $ symbol, currency is USD
- If amounts use EUR or euro, currency is EUR
- If amounts use GBP or pound or pounds, currency is GBP
- If "tax rate: N%" is mentioned, apply that tax rate (as decimal N/100) to ALL line items

Return ONLY a valid JSON object with these fields.
"""

        try:
            data = await self._text_generator.generate_structured(
                prompt=extraction_prompt,
                output_schema=self.EXTRACTION_SCHEMA,
                max_tokens=2000
            )

            return self._parse_ai_data(data)

        except Exception as e:
            logger.error(f"AI extraction failed with exception: {e}")
            # Return empty result; merge will use regex results
            return InvoiceExtractionResult(
                invoice_number="", client_name="", client_address="",
                vendor_name="", vendor_address="", currency="",
                payment_terms="", notes="", line_items=[]
            )

    def _parse_ai_data(self, data: Dict[str, Any]) -> InvoiceExtractionResult:
        """
        Parse AI-extracted data into InvoiceExtractionResult.

        Args:
            data: Extracted data dictionary from AI

        Returns:
            InvoiceExtractionResult
        """
        # Parse line items
        line_items = []
        for item_data in data.get("line_items", []):
            try:
                item = InvoiceLineItemExtraction(
                    description=item_data.get("description", ""),
                    quantity=float(item_data.get("quantity", 1)),
                    unit_price=float(item_data.get("unit_price", 0)),
                    tax_rate=float(item_data.get("tax_rate", 0))
                )
                if item.description:
                    line_items.append(item)
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse AI line item: {e}")
                continue

        inv_number = data.get("invoice_number", "")
        if not inv_number:
            inv_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        return InvoiceExtractionResult(
            invoice_number=inv_number,
            client_name=data.get("client_name", ""),
            client_address=data.get("client_address", ""),
            vendor_name=data.get("vendor_name", ""),
            vendor_address=data.get("vendor_address", ""),
            currency=data.get("currency", ""),
            payment_terms=data.get("payment_terms", ""),
            notes=data.get("notes", ""),
            line_items=line_items
        )

    def _regex_extraction(self, user_prompt: str) -> InvoiceExtractionResult:
        """
        Extract invoice data using regex patterns.
        This is the reliable baseline that always runs.

        Args:
            user_prompt: User's prompt

        Returns:
            Extracted invoice data
        """
        prompt_lower = user_prompt.lower()

        # Extract vendor name and address
        vendor_name, vendor_address = self._extract_vendor(user_prompt)

        # Extract client name and address
        client_name, client_address = self._extract_client(user_prompt)

        # Extract currency
        currency = "USD"
        if "eur" in prompt_lower or "euro" in prompt_lower or "\u20ac" in user_prompt:
            currency = "EUR"
        elif "gbp" in prompt_lower or "pound" in prompt_lower or "\u00a3" in user_prompt:
            currency = "GBP"

        # Extract tax rate
        tax_rate = 0.0
        tax_match = re.search(r'tax(?:\s+rate)?[:\s]+(\d+(?:\.\d+)?)\s*%', user_prompt, re.IGNORECASE)
        if tax_match:
            tax_rate = float(tax_match.group(1)) / 100

        # Extract payment terms
        payment_terms = ""
        payment_match = re.search(r'payment\s+terms?[:\s]+([^\.]+?)(?:\.|$)', user_prompt, re.IGNORECASE)
        if payment_match:
            payment_terms = payment_match.group(1).strip()

        # Extract notes - greedy match up to next labeled field or end of string
        notes = ""
        notes_match = re.search(
            r'notes?[:\s]+\s*(.+?)(?:\s*(?:payment|tax|items?|vendor|customer|client)[:\s]|$)',
            user_prompt, re.IGNORECASE | re.DOTALL
        )
        if notes_match:
            notes = notes_match.group(1).strip().rstrip('.')

        # Extract line items
        line_items = self._extract_line_items_regex(user_prompt, tax_rate)

        inv_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        return InvoiceExtractionResult(
            invoice_number=inv_number,
            client_name=client_name,
            client_address=client_address,
            vendor_name=vendor_name,
            vendor_address=vendor_address,
            currency=currency,
            payment_terms=payment_terms,
            notes=notes,
            line_items=line_items
        )

    def _extract_vendor(self, user_prompt: str) -> tuple:
        """Extract vendor name and address from prompt."""
        vendor_name = ""
        vendor_address = ""

        # Pattern 1: "Vendor: Name, Address..." (case insensitive)
        vendor_label = re.search(
            r'vendor[:\s]+\s*([^\.]+?)(?:\.\s|$)',
            user_prompt, re.IGNORECASE
        )
        if vendor_label:
            full_text = vendor_label.group(1).strip()
            parts = full_text.split(',')
            vendor_name = parts[0].strip()
            if len(parts) > 1:
                vendor_address = ', '.join(p.strip() for p in parts[1:])
            return vendor_name, vendor_address

        # Pattern 2: "from CompanyName to ..." (case insensitive)
        from_match = re.search(
            r'\bfrom\s+([A-Z][A-Za-z0-9\s&.]+?)(?:\s+to\s|\s+for\s|,|\.|$)',
            user_prompt, re.IGNORECASE
        )
        if from_match:
            vendor_name = from_match.group(1).strip().rstrip(',.')
            return vendor_name, vendor_address

        return vendor_name, vendor_address

    def _extract_client(self, user_prompt: str) -> tuple:
        """Extract client name and address from prompt."""
        client_name = ""
        client_address = ""

        # Pattern 1: "Customer: ..." or "Client: ..." (case insensitive)
        client_label = re.search(
            r'(?:customer|client)[:\s]+\s*([^\.]+?)(?:\.\s|$)',
            user_prompt, re.IGNORECASE
        )
        if client_label:
            full_text = client_label.group(1).strip()
            # Handle "PersonName at CompanyName, Address"
            if ' at ' in full_text:
                at_parts = full_text.split(' at ', 1)
                person_name = at_parts[0].strip()
                rest = at_parts[1].strip()
                # Split rest into company and address
                comma_parts = rest.split(',')
                company_name = comma_parts[0].strip()
                client_name = f"{person_name} at {company_name}"
                if len(comma_parts) > 1:
                    client_address = ', '.join(p.strip() for p in comma_parts[1:])
            else:
                # "Client: CompanyName, Address"
                parts = full_text.split(',')
                client_name = parts[0].strip()
                if len(parts) > 1:
                    client_address = ', '.join(p.strip() for p in parts[1:])
            return client_name, client_address

        # Pattern 2: "to CompanyName for ..." or "bill to CompanyName"
        to_match = re.search(
            r'(?:\bto\b|bill\s+to)[:\s]+\s*([A-Z][A-Za-z0-9\s&.]+?)(?:\s+for\s|\s+invoice|,|\.|$)',
            user_prompt, re.IGNORECASE
        )
        if to_match:
            client_name = to_match.group(1).strip().rstrip(',.')
            return client_name, client_address

        return client_name, client_address

    def _extract_line_items_regex(
        self, user_prompt: str, default_tax_rate: float = 0.0
    ) -> List[InvoiceLineItemExtraction]:
        """Extract line items from prompt using regex patterns."""
        items = []

        # Pattern 1: "Items: ItemName ($price x qty), ..." block
        items_block = re.search(
            r'items?[:\s]+\s*([^\.]+?)(?:\.\s|\.\s*$|$)',
            user_prompt, re.IGNORECASE
        )
        if items_block:
            item_pattern = r'([^(,]+?)\s*\(\s*\$?([\d.]+)\s*x\s*(\d+)\s*\)'
            for desc, price, qty in re.findall(item_pattern, items_block.group(1)):
                desc_clean = desc.strip().rstrip(',').strip()
                if desc_clean:
                    items.append(InvoiceLineItemExtraction(
                        description=desc_clean,
                        quantity=float(qty),
                        unit_price=float(price),
                        tax_rate=default_tax_rate
                    ))

        # Pattern 2: X hours/units of Y at $Z per hour/each
        if not items:
            pattern_hours = re.findall(
                r'(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|units?)\s+(?:of\s+)?(.+?)\s+at\s+\$?(\d+(?:[\.,]\d+)?)\s*(?:per\s+hour|/\s*h(?:ou)?r|each|per\s+unit)?',
                user_prompt, re.IGNORECASE
            )
            for qty, desc, price in pattern_hours:
                desc_clean = desc.strip().rstrip(',').strip()
                if desc_clean:
                    items.append(InvoiceLineItemExtraction(
                        description=desc_clean,
                        quantity=float(qty),
                        unit_price=float(price.replace(',', '')),
                        tax_rate=default_tax_rate
                    ))

        # Pattern 3: X <description> at $Y each/per unit
        if not items:
            pattern_qty = re.findall(
                r'(\d+(?:\.\d+)?)\s+([a-zA-Z][a-zA-Z\s]+?)\s+at\s+\$?(\d+(?:[\.,]\d+)?)\s*(?:each|per\s+unit|apiece)?',
                user_prompt, re.IGNORECASE
            )
            for qty, desc, price in pattern_qty:
                desc_clean = desc.strip().rstrip(',').strip()
                if desc_clean and not any(i.description.lower() == desc_clean.lower() for i in items):
                    items.append(InvoiceLineItemExtraction(
                        description=desc_clean,
                        quantity=float(qty),
                        unit_price=float(price.replace(',', '')),
                        tax_rate=default_tax_rate
                    ))

        return items

    def _fill_defaults(self, result: InvoiceExtractionResult) -> InvoiceExtractionResult:
        """
        Fill remaining empty fields with reasonable defaults.
        Only called after regex + AI merge, so these are true last-resort defaults.

        Args:
            result: The extraction result to fill

        Returns:
            InvoiceExtractionResult with all fields populated
        """
        if not result.client_name:
            result.client_name = "Client Company LLC"
        if not result.client_address:
            result.client_address = "123 Business Ave\nNew York, NY 10001"
        if not result.vendor_name:
            result.vendor_name = "Professional Services Inc"
        if not result.vendor_address:
            result.vendor_address = "456 Commerce St\nSan Francisco, CA 94102"
        if not result.currency:
            result.currency = "USD"
        if not result.payment_terms:
            result.payment_terms = "Net 30 days"
        if not result.notes:
            result.notes = "Thank you for your business!"

        # Generate contextual default line items if none were extracted
        if not result.line_items:
            result.line_items = self._generate_default_line_items(result)

        # Validate line item values
        for item in result.line_items:
            if item.quantity <= 0:
                item.quantity = 1
            if item.unit_price < 0:
                item.unit_price = 0
            if not (0 <= item.tax_rate <= 1):
                if 1 < item.tax_rate <= 100:
                    item.tax_rate = item.tax_rate / 100
                else:
                    item.tax_rate = 0.0

        return result

    def _generate_default_line_items(
        self, result: InvoiceExtractionResult
    ) -> List[InvoiceLineItemExtraction]:
        """Generate default line items based on context from extracted data."""
        return [
            InvoiceLineItemExtraction("Professional Services", 10, 150.00, 0.0),
            InvoiceLineItemExtraction("Consultation Hours", 5, 200.00, 0.0),
        ]

    def get_status(self) -> Dict[str, Any]:
        """Get analyzer status information."""
        return {
            "text_generator_active": self._text_generator.is_active,
            "text_generator_model": self._text_generator.model_name,
            "extraction_mode": "AI + Regex" if self._text_generator.is_active else "Regex only"
        }
