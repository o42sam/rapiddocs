"""
Invoice generation service using AI to create realistic invoice data
"""
import json
import re
from datetime import datetime, timedelta
from typing import List
from app.services.text_generation import text_generation_service
from app.schemas.invoice import InvoiceData, InvoiceLineItem
from app.models.document import Statistic
from app.utils.logger import get_logger
from app.utils.exceptions import TextGenerationError

logger = get_logger('invoice_generator')


class InvoiceGeneratorService:
    """Service to generate invoice data using AI"""

    def generate_invoice_data(
        self,
        description: str,
        statistics: List[Statistic]
    ) -> InvoiceData:
        """
        Generate complete invoice data based on user description and statistics

        Args:
            description: User's description of what the invoice should be for
            statistics: Optional statistics that can inform pricing/quantities

        Returns:
            InvoiceData object with all invoice information
        """
        logger.info("Generating invoice data from description")

        # Create prompt for AI to generate invoice JSON
        prompt = self._create_invoice_prompt(description, statistics)

        try:
            # Generate invoice data using the text generation service's HuggingFace client
            if hasattr(text_generation_service, 'hf_client') and text_generation_service.hf_client:
                # Use HuggingFace InferenceClient with chat completions API
                response_obj = text_generation_service.hf_client.chat.completions.create(
                    model=text_generation_service.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7,
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
                            "max_new_tokens": 2000,
                            "temperature": 0.7,
                            "top_p": 0.95,
                            "return_full_text": False
                        }
                    }
                    api_response = requests.post(
                        text_generation_service.api_url,
                        json=payload,
                        headers=text_generation_service.headers,
                        timeout=300
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
                            "temperature": 0.7,
                            "top_p": 0.95,
                            "num_predict": 2000,
                        }
                    }
                    api_response = requests.post(
                        text_generation_service.api_url,
                        json=payload,
                        headers=text_generation_service.headers,
                        timeout=300
                    )
                    api_response.raise_for_status()
                    result = api_response.json()
                    response = result.get("response", "")

            logger.debug(f"Raw AI response: {response}")

            # Extract JSON from response
            invoice_json = self._extract_json_from_response(response)
            logger.debug(f"Extracted JSON: {invoice_json}")

            # Parse and validate invoice data
            invoice_data = self._parse_invoice_json(invoice_json)

            # Calculate and verify totals
            invoice_data = self._calculate_totals(invoice_data)

            logger.info(f"Successfully generated invoice: {invoice_data.invoice_number}")
            return invoice_data

        except Exception as e:
            logger.error(f"Failed to generate invoice data: {str(e)}")
            # Fallback to generating a basic invoice
            return self._generate_fallback_invoice(description, statistics)

    def _create_invoice_prompt(self, description: str, statistics: List[Statistic]) -> str:
        """Create a prompt for AI to generate invoice JSON"""

        stats_context = ""
        if statistics:
            stats_context = "\n\nUse these statistics to inform quantities and pricing:\n"
            for stat in statistics:
                stats_context += f"- {stat.name}: {stat.value} {stat.unit or ''}\n"

        current_date = datetime.now().strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        prompt = f"""Generate a professional invoice based on this description: {description}
{stats_context}

IMPORTANT INSTRUCTIONS:
1. Extract business information (company name, address, contact details) from the description if provided
2. Extract invoice date from description if provided, otherwise use today's date ({current_date})
3. Extract line items with their prices and quantities from the description if provided
4. If prices/quantities are given in the description (e.g., "$45 x 2"), use those exact values
5. Extract customer/client name from the description if provided
6. Generate realistic values only for missing information
7. Calculate accurate totals based on the line items

Create a JSON object with the following structure. Return ONLY valid JSON, no other text:

{{
  "invoice_number": "INV-2025-XXXX",
  "invoice_date": "{current_date}",
  "due_date": "{due_date}",
  "bill_from_name": "Company Name (extract from description or create realistic name)",
  "bill_from_address": "Full business address (extract from description or create realistic address)",
  "bill_from_email": "billing@company.com",
  "bill_from_phone": "+1 (555) 123-4567",
  "bill_to_name": "Client Name (extract from description or create realistic client name)",
  "bill_to_address": "Client full address",
  "bill_to_email": "client@email.com",
  "bill_to_phone": "+1 (555) 987-6543",
  "line_items": [
    {{
      "description": "Specific service or product name - be detailed",
      "quantity": 10.0,
      "unit_price": 150.00,
      "amount": 1500.00
    }}
  ],
  "subtotal": 1500.00,
  "tax_rate": 8.5,
  "tax_amount": 127.50,
  "discount_amount": 0.00,
  "total": 1627.50,
  "payment_terms": "Net 30",
  "notes": "Thank you for your business!"
}}

For: {description}

Return ONLY the JSON object, no explanations or markdown formatting."""

        return prompt

    def _extract_json_from_response(self, response: str) -> dict:
        """Extract JSON from AI response, handling markdown and extra text"""
        # Remove markdown code blocks if present
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)

        # Find JSON object
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in response")

        json_str = json_match.group(0)

        # Parse JSON
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            logger.error(f"Attempted to parse: {json_str}")
            raise

    def _parse_invoice_json(self, json_data: dict) -> InvoiceData:
        """Parse and validate invoice JSON data"""

        # Parse line items
        line_items = []
        for item_data in json_data.get('line_items', []):
            item = InvoiceLineItem(**item_data)
            line_items.append(item)

        # Create invoice data object with proper defaults
        invoice_data = InvoiceData(
            invoice_number=json_data.get('invoice_number', 'INV-2025-0001'),
            invoice_date=json_data.get('invoice_date', datetime.now().strftime("%Y-%m-%d")),
            due_date=json_data.get('due_date', (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")),
            bill_from_name=json_data.get('bill_from_name', 'Your Company'),
            bill_from_address=json_data.get('bill_from_address') or None,
            bill_from_email=json_data.get('bill_from_email') or None,
            bill_from_phone=json_data.get('bill_from_phone') or None,
            bill_to_name=json_data.get('bill_to_name', 'Client Name'),
            bill_to_address=json_data.get('bill_to_address') or None,
            bill_to_email=json_data.get('bill_to_email') or None,
            bill_to_phone=json_data.get('bill_to_phone') or None,
            line_items=line_items,
            subtotal=json_data.get('subtotal', 0.0),
            tax_rate=json_data.get('tax_rate', 0.0),
            tax_amount=json_data.get('tax_amount', 0.0),
            discount_amount=json_data.get('discount_amount', 0.0),
            total=json_data.get('total', 0.0),
            payment_terms=json_data.get('payment_terms') or 'Net 30',
            notes=json_data.get('notes') or None
        )

        return invoice_data

    def _calculate_totals(self, invoice_data: InvoiceData) -> InvoiceData:
        """Recalculate and verify invoice totals"""

        # Calculate subtotal from line items
        calculated_subtotal = sum(item.calculated_amount for item in invoice_data.line_items)

        # Calculate tax
        calculated_tax = calculated_subtotal * (invoice_data.tax_rate / 100)

        # Calculate total
        calculated_total = calculated_subtotal + calculated_tax - invoice_data.discount_amount

        # Update invoice data with calculated values
        invoice_data.subtotal = round(calculated_subtotal, 2)
        invoice_data.tax_amount = round(calculated_tax, 2)
        invoice_data.total = round(calculated_total, 2)

        # Also update line item amounts to be consistent
        for item in invoice_data.line_items:
            item.amount = round(item.calculated_amount, 2)

        return invoice_data

    def _generate_fallback_invoice(
        self,
        description: str,
        statistics: List[Statistic]
    ) -> InvoiceData:
        """Generate a basic fallback invoice if AI generation fails"""
        logger.warning("Using fallback invoice generation")

        # Extract some keywords from description for item names
        words = description.split()[:3] if description else []
        service_name = " ".join(words).title() if words else "Professional Services"

        # Create basic line items
        line_items = [
            InvoiceLineItem(
                description=f"{service_name} - Initial Setup",
                quantity=1.0,
                unit_price=500.00,
                amount=500.00
            ),
            InvoiceLineItem(
                description=f"{service_name} - Monthly Service (3 months)",
                quantity=3.0,
                unit_price=250.00,
                amount=750.00
            ),
            InvoiceLineItem(
                description="Additional Support and Maintenance",
                quantity=10.0,
                unit_price=75.00,
                amount=750.00
            )
        ]

        # Add items based on statistics if available
        if statistics:
            for stat in statistics[:3]:  # Use up to 3 statistics
                line_items.append(
                    InvoiceLineItem(
                        description=f"{stat.name} Services",
                        quantity=float(stat.value) if stat.value < 100 else 1.0,
                        unit_price=99.99 if stat.value < 100 else stat.value,
                        amount=0.0  # Will be calculated
                    )
                )

        invoice_data = InvoiceData(
            invoice_number=f"INV-{datetime.now().strftime('%Y%m%d')}-001",
            invoice_date=datetime.now().strftime("%Y-%m-%d"),
            due_date=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            bill_from_name="Your Company Name",
            bill_from_address="123 Business Street, Suite 100\nCity, State 12345",
            bill_from_email="billing@yourcompany.com",
            bill_from_phone="+1 (555) 123-4567",
            bill_to_name="Client Company",
            bill_to_address="456 Client Avenue\nClient City, State 67890",
            bill_to_email="accounts@client.com",
            bill_to_phone="+1 (555) 987-6543",
            line_items=line_items,
            subtotal=0.0,
            tax_rate=8.5,
            tax_amount=0.0,
            discount_amount=0.0,
            total=0.0,
            payment_terms="Net 30 days",
            notes="Thank you for your business! Payment is due within 30 days."
        )

        # Calculate totals
        return self._calculate_totals(invoice_data)


# Singleton instance
invoice_generator_service = InvoiceGeneratorService()
