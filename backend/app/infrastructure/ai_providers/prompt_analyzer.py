"""
Prompt Analyzer for Infographic Document Generation.
Extracts structured data from user prompts using Gemini AI.
"""

import re
import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

from .gemini_text_generator import GeminiTextGenerator
from ...shared.logger import get_logger

logger = get_logger("prompt_analyzer")


@dataclass
class StatisticExtraction:
    """Extracted statistic from user prompt."""
    name: str
    value: float
    unit: str
    visualization_type: str  # bar_chart, line_chart, pie_chart, gauge_chart, number
    category: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "visualization_type": self.visualization_type,
            "category": self.category,
            "description": self.description
        }


@dataclass
class InfographicExtractionResult:
    """Result of extracting infographic data from user prompt."""
    title: str
    topic: str
    word_count: int
    num_sections: int
    statistics: List[StatisticExtraction]
    image_prompts: List[str]
    section_outlines: List[str]
    color_suggestions: List[str] = field(default_factory=list)
    tone: str = "professional"
    date: str = field(default_factory=lambda: datetime.now().strftime("%B %d, %Y"))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "topic": self.topic,
            "word_count": self.word_count,
            "num_sections": self.num_sections,
            "statistics": [s.to_dict() for s in self.statistics],
            "image_prompts": self.image_prompts,
            "section_outlines": self.section_outlines,
            "color_suggestions": self.color_suggestions,
            "tone": self.tone,
            "date": self.date
        }


class PromptAnalyzer:
    """
    Analyzes user prompts to extract structured data for infographic generation.
    Uses Gemini AI for intelligent extraction with fallback parsing.
    """

    EXTRACTION_SCHEMA = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Document title"},
            "topic": {"type": "string", "description": "Main topic/subject"},
            "word_count": {"type": "integer", "description": "Target word count"},
            "num_sections": {"type": "integer", "description": "Number of sections"},
            "tone": {"type": "string", "description": "Document tone"},
            "statistics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "value": {"type": "number"},
                        "unit": {"type": "string"},
                        "visualization_type": {"type": "string"},
                        "category": {"type": "string"},
                        "description": {"type": "string"}
                    }
                }
            },
            "image_prompts": {
                "type": "array",
                "items": {"type": "string"}
            },
            "section_outlines": {
                "type": "array",
                "items": {"type": "string"}
            },
            "color_suggestions": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    }

    def __init__(self, text_generator: GeminiTextGenerator):
        """
        Initialize the prompt analyzer.

        Args:
            text_generator: Gemini text generator for AI-powered extraction
        """
        self._text_generator = text_generator
        logger.info("Prompt Analyzer initialized")
        logger.info(f"Using text generator: {text_generator.provider_name} - {text_generator.model_name}")
        logger.info(f"Text generator active: {text_generator.is_active}")

    async def analyze(self, user_prompt: str) -> InfographicExtractionResult:
        """
        Analyze a user prompt and extract structured infographic data.

        Args:
            user_prompt: The user's description/prompt for the infographic

        Returns:
            InfographicExtractionResult with extracted data
        """
        logger.info("=" * 50)
        logger.info("PROMPT ANALYSIS STARTED")
        logger.info("=" * 50)
        logger.info(f"Input prompt length: {len(user_prompt)} characters")

        if self._text_generator.is_active:
            logger.info("Using AI-powered extraction")
            result = await self._ai_extraction(user_prompt)
        else:
            logger.info("Using fallback regex extraction")
            result = self._fallback_extraction(user_prompt)

        logger.info("EXTRACTION RESULTS:")
        logger.info(f"  Title: {result.title}")
        logger.info(f"  Topic: {result.topic}")
        logger.info(f"  Word Count: {result.word_count}")
        logger.info(f"  Sections: {result.num_sections}")
        logger.info(f"  Statistics: {len(result.statistics)}")
        logger.info(f"  Image Prompts: {len(result.image_prompts)}")
        logger.info("=" * 50)

        return result

    async def _ai_extraction(self, user_prompt: str) -> InfographicExtractionResult:
        """
        Extract data using AI.

        Args:
            user_prompt: User's prompt

        Returns:
            Extracted infographic data
        """
        extraction_prompt = f"""
You are an expert document analyzer. Analyze the following user prompt for generating
an infographic document and extract structured information.

USER PROMPT:
{user_prompt}

Extract the following information:

1. title: A clear, professional document title
2. topic: The main subject matter
3. word_count: Target word count (look for "X words", "approximately X words", or infer:
   - "brief"/"short" = 300-500
   - "detailed"/"comprehensive" = 1000-2000
   - default = 500 if not specified)
4. num_sections: Number of sections (infer from content complexity, typically 3-5)
5. tone: One of: professional, academic, business, formal (default: professional)
6. statistics: Array of statistics mentioned, each with:
   - name: What the statistic measures
   - value: Numeric value
   - unit: Unit of measurement (%, USD, items, etc.)
   - visualization_type: Best chart type (bar_chart, line_chart, pie_chart, gauge_chart, number)
   - category: Optional grouping category
   - description: Brief description
7. image_prompts: Generate 3-4 descriptive prompts for illustrations that would complement
   each section. Make them specific and visually descriptive.
8. section_outlines: Brief outline/title for each section
9. color_suggestions: 3 hex color codes that match the topic theme

For visualization_type selection:
- Use "bar_chart" for comparisons between categories
- Use "line_chart" for trends over time
- Use "pie_chart" for parts of a whole (percentages that sum to 100)
- Use "gauge_chart" for single percentage/progress values
- Use "number" for standalone important figures

Return ONLY a valid JSON object with these fields.
"""

        try:
            data = await self._text_generator.generate_structured(
                prompt=extraction_prompt,
                output_schema=self.EXTRACTION_SCHEMA,
                max_tokens=2000
            )

            return self._parse_extraction_data(data, user_prompt)

        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            return self._fallback_extraction(user_prompt)

    def _parse_extraction_data(
        self,
        data: Dict[str, Any],
        original_prompt: str
    ) -> InfographicExtractionResult:
        """
        Parse extracted data into InfographicExtractionResult.

        Args:
            data: Extracted data dictionary
            original_prompt: Original user prompt for fallback values

        Returns:
            InfographicExtractionResult
        """
        # Parse statistics
        statistics = []
        for stat_data in data.get("statistics", []):
            try:
                stat = StatisticExtraction(
                    name=stat_data.get("name", "Statistic"),
                    value=float(stat_data.get("value", 0)),
                    unit=stat_data.get("unit", "units"),
                    visualization_type=stat_data.get("visualization_type", "bar_chart"),
                    category=stat_data.get("category"),
                    description=stat_data.get("description")
                )
                statistics.append(stat)
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse statistic: {e}")
                continue

        # Extract word count from original prompt if not in data
        word_count = data.get("word_count", 500)
        word_match = re.search(r'(\d+)\s*words?', original_prompt.lower())
        if word_match:
            word_count = int(word_match.group(1))

        # Validate word count bounds
        word_count = max(200, min(word_count, 5000))

        # Get num_sections with reasonable default
        num_sections = data.get("num_sections", 3)
        num_sections = max(2, min(num_sections, 8))

        # Ensure we have image prompts
        image_prompts = data.get("image_prompts", [])
        if not image_prompts:
            topic = data.get("topic", original_prompt[:100])
            image_prompts = self._generate_default_image_prompts(topic, num_sections)

        # Ensure we have section outlines
        section_outlines = data.get("section_outlines", [])
        if not section_outlines:
            section_outlines = self._generate_default_section_outlines(
                data.get("topic", "the topic"),
                num_sections
            )

        return InfographicExtractionResult(
            title=data.get("title", self._extract_title(original_prompt)),
            topic=data.get("topic", original_prompt[:200]),
            word_count=word_count,
            num_sections=num_sections,
            statistics=statistics,
            image_prompts=image_prompts,
            section_outlines=section_outlines,
            color_suggestions=data.get("color_suggestions", ["#1e40af", "#3730a3", "#7c3aed"]),
            tone=data.get("tone", "professional")
        )

    def _fallback_extraction(self, user_prompt: str) -> InfographicExtractionResult:
        """
        Extract data using regex patterns when AI is unavailable.

        Args:
            user_prompt: User's prompt

        Returns:
            Extracted infographic data
        """
        logger.info("Using fallback extraction (no AI)")

        # Extract word count
        word_count = 500
        word_match = re.search(r'(\d+)\s*words?', user_prompt.lower())
        if word_match:
            word_count = int(word_match.group(1))
        elif "brief" in user_prompt.lower() or "short" in user_prompt.lower():
            word_count = 300
        elif "detailed" in user_prompt.lower() or "comprehensive" in user_prompt.lower():
            word_count = 1500

        # Extract title
        title = self._extract_title(user_prompt)

        # Extract topic (first sentence or up to 200 chars)
        topic = user_prompt.split('.')[0][:200] if '.' in user_prompt else user_prompt[:200]

        # Extract statistics using regex
        statistics = self._extract_statistics_regex(user_prompt)

        # Determine number of sections
        num_sections = 3
        if word_count > 1000:
            num_sections = 5
        elif word_count > 500:
            num_sections = 4

        # Generate section outlines
        section_outlines = self._generate_default_section_outlines(topic, num_sections)

        # Generate image prompts
        image_prompts = self._generate_default_image_prompts(topic, num_sections)

        return InfographicExtractionResult(
            title=title,
            topic=topic,
            word_count=word_count,
            num_sections=num_sections,
            statistics=statistics,
            image_prompts=image_prompts,
            section_outlines=section_outlines,
            color_suggestions=["#1e40af", "#3730a3", "#7c3aed"],
            tone="professional"
        )

    def _extract_title(self, prompt: str) -> str:
        """Extract a title from the prompt."""
        # Try common patterns
        patterns = [
            r'(?:titled?|about|regarding|on)\s+["\']?([^"\'\.]+)["\']?',
            r'^([A-Z][^\.]{10,50})',
        ]

        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:100]

        # Generate title from first few words
        words = prompt.split()[:8]
        return " ".join(words).title()

    def _extract_statistics_regex(self, prompt: str) -> List[StatisticExtraction]:
        """Extract statistics using regex patterns."""
        statistics = []

        # Pattern for percentages
        percent_pattern = r'(\d+(?:\.\d+)?)\s*%\s*(?:of\s+)?([^,\.]+)'
        for match in re.finditer(percent_pattern, prompt):
            value = float(match.group(1))
            name = match.group(2).strip()[:50]
            statistics.append(StatisticExtraction(
                name=name,
                value=value,
                unit="%",
                visualization_type="gauge_chart" if value <= 100 else "bar_chart"
            ))

        # Pattern for currency
        currency_pattern = r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:for|in|of)?\s*([^,\.]+)?'
        for match in re.finditer(currency_pattern, prompt):
            value = float(match.group(1).replace(',', ''))
            name = match.group(2).strip()[:50] if match.group(2) else "Revenue"
            statistics.append(StatisticExtraction(
                name=name,
                value=value,
                unit="USD",
                visualization_type="bar_chart"
            ))

        # Pattern for general numbers with context
        number_pattern = r'(\d+(?:,\d{3})*)\s+(users?|customers?|items?|products?|employees?|sales?|orders?)'
        for match in re.finditer(number_pattern, prompt, re.IGNORECASE):
            value = float(match.group(1).replace(',', ''))
            unit = match.group(2).lower()
            statistics.append(StatisticExtraction(
                name=unit.title(),
                value=value,
                unit=unit,
                visualization_type="number"
            ))

        return statistics

    def _generate_default_image_prompts(self, topic: str, num_sections: int) -> List[str]:
        """Generate default image prompts based on topic."""
        base_prompts = [
            f"Professional infographic illustration showing {topic}, modern clean design, business style",
            f"Abstract visualization representing {topic}, geometric shapes, corporate colors",
            f"Conceptual illustration of {topic}, minimalist style, professional aesthetic",
            f"Data-driven visual representation of {topic}, charts and icons, modern design"
        ]

        # Return prompts matching the number of sections
        return base_prompts[:min(num_sections, 4)]

    def _generate_default_section_outlines(self, topic: str, num_sections: int) -> List[str]:
        """Generate default section outlines."""
        default_outlines = [
            f"Introduction to {topic}",
            f"Key Aspects and Analysis",
            f"Current Trends and Data",
            f"Implications and Impact",
            f"Future Outlook",
            f"Conclusions and Recommendations"
        ]

        return default_outlines[:num_sections]

    def get_status(self) -> Dict[str, Any]:
        """Get analyzer status information."""
        return {
            "text_generator_active": self._text_generator.is_active,
            "text_generator_model": self._text_generator.model_name,
            "extraction_mode": "AI" if self._text_generator.is_active else "Fallback"
        }
