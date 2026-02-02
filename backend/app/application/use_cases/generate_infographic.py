"""
Generate Infographic Use Case.
Orchestrates the entire infographic document generation workflow.
"""

import uuid
import asyncio
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime

from ..dto.infographic_request import InfographicRequest, StatisticDTO
from ...domain.interfaces.text_generator import ITextGenerator
from ...domain.interfaces.image_generator import IImageGenerator
from ...domain.interfaces.visualization_engine import IVisualizationEngine
from ...domain.interfaces.data_importer import IDataImporter
from ...infrastructure.ai_providers.prompt_analyzer import PromptAnalyzer, InfographicExtractionResult
from ...infrastructure.document_renderers.infographic_pdf_renderer import InfographicPDFRenderer
from ...shared.logger import get_logger
from ...config import settings

logger = get_logger("generate_infographic")


class GenerateInfographicUseCase:
    """
    Use case for generating infographic documents.

    This is the central orchestrator that coordinates:
    1. Prompt analysis and data extraction (via Gemini)
    2. Text content generation (via Gemini)
    3. Statistics visualization (via Matplotlib)
    4. Illustration generation (via Nano Banana/HuggingFace)
    5. PDF rendering (via ReportLab)

    The Gemini model is at the center, extracting data from user prompts
    and generating content that flows to all other components.
    """

    # System prompt for content generation
    CONTENT_GENERATION_PROMPT = """
You are a professional document writer creating content for an infographic document.

CRITICAL FORMATTING RULES:
1. NEVER use bullet points (•, -, *, etc.) for any enumeration
2. Use ONLY these enumeration styles:
   - Numbers (1, 2, 3) for main points and sections
   - Letters (a, b, c) for sub-points
   - Roman numerals (i, ii, iii) for sub-sub-points
3. Write in a professional, informative tone
4. Each paragraph should be substantive and detailed
5. Naturally incorporate any statistics mentioned
6. Use proper paragraph structure with clear topic sentences

DOCUMENT SPECIFICATIONS:
Title: {title}
Topic: {topic}
Target Word Count: {word_count} words
Number of Sections: {num_sections}
Tone: {tone}

Section Outlines:
{section_outlines}

Statistics to Include:
{statistics}

Generate professional, well-structured content that:
- Has a clear introduction explaining the topic
- Covers each section outlined above in detail
- Incorporates the statistics naturally within the text
- Concludes with a summary of key points
- Meets the target word count of {word_count} words

Begin generating the content now:
"""

    def __init__(
        self,
        text_generator: ITextGenerator,
        image_generator: IImageGenerator,
        visualization_engine: IVisualizationEngine,
        document_renderer: InfographicPDFRenderer,
        prompt_analyzer: PromptAnalyzer,
        data_importer: Optional[IDataImporter] = None
    ):
        """
        Initialize the use case with required dependencies.

        Args:
            text_generator: For generating document text content
            image_generator: For generating illustrations
            visualization_engine: For creating charts and graphs
            document_renderer: For rendering the final PDF
            prompt_analyzer: For extracting data from user prompts
            data_importer: Optional importer for CSV/Excel data
        """
        self._text_generator = text_generator
        self._image_generator = image_generator
        self._visualization_engine = visualization_engine
        self._document_renderer = document_renderer
        self._prompt_analyzer = prompt_analyzer
        self._data_importer = data_importer

        self._output_dir = Path(settings.PDF_OUTPUT_DIR)
        self._output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 70)
        logger.info("GENERATE INFOGRAPHIC USE CASE INITIALIZED")
        logger.info("=" * 70)
        self._log_component_status()

    def _log_component_status(self) -> None:
        """Log the status of all components."""
        logger.info("Component Status:")
        logger.info(f"  Text Generator: {self._text_generator.provider_name} - "
                   f"{self._text_generator.model_name}")

        # Check if components have is_active property
        if hasattr(self._text_generator, 'is_active'):
            logger.info(f"    Status: {'ACTIVE' if self._text_generator.is_active else 'INACTIVE'}")

        if hasattr(self._image_generator, 'is_active'):
            logger.info(f"  Image Generator: "
                       f"{'ACTIVE' if self._image_generator.is_active else 'INACTIVE'}")
        else:
            logger.info(f"  Image Generator: {self._image_generator.model_name}")

        if hasattr(self._visualization_engine, 'is_active'):
            logger.info(f"  Visualization Engine: "
                       f"{'ACTIVE' if self._visualization_engine.is_active else 'INACTIVE'}")
        else:
            logger.info("  Visualization Engine: Matplotlib (ACTIVE)")

        logger.info(f"  Document Renderer: InfographicPDFRenderer (ACTIVE)")
        logger.info(f"  Output Directory: {self._output_dir}")
        logger.info("=" * 70)

    async def execute(self, request: InfographicRequest) -> Path:
        """
        Execute the infographic generation workflow.

        Args:
            request: InfographicRequest with generation parameters

        Returns:
            Path to the generated PDF file
        """
        job_id = str(uuid.uuid4())[:8]
        logger.info("=" * 70)
        logger.info(f"INFOGRAPHIC GENERATION STARTED - Job ID: {job_id}")
        logger.info("=" * 70)
        logger.info(f"Title: {request.title}")
        logger.info(f"Topic: {request.topic[:100]}...")

        try:
            # Step 1: Analyze prompt and extract structured data
            logger.info("\n[STEP 1/5] Analyzing prompt and extracting data...")
            extraction = await self._analyze_prompt(request)

            # Step 2: Generate text content
            logger.info("\n[STEP 2/5] Generating document text content...")
            sections = await self._generate_text_content(extraction, request)

            # Step 3: Generate visualizations for statistics
            logger.info("\n[STEP 3/5] Generating charts and visualizations...")
            charts = await self._generate_visualizations(extraction, request, job_id)

            # Step 4: Generate illustrations
            logger.info("\n[STEP 4/5] Generating illustrations...")
            illustrations = await self._generate_illustrations(extraction, request, job_id)

            # Step 5: Render final PDF
            logger.info("\n[STEP 5/5] Rendering final PDF document...")
            output_path = await self._render_document(
                extraction, sections, charts, illustrations, request, job_id
            )

            logger.info("=" * 70)
            logger.info(f"INFOGRAPHIC GENERATION COMPLETE - Job ID: {job_id}")
            logger.info(f"Output: {output_path}")
            logger.info("=" * 70)

            return output_path

        except Exception as e:
            logger.error(f"Infographic generation failed: {e}")
            raise

    async def _analyze_prompt(
        self,
        request: InfographicRequest
    ) -> InfographicExtractionResult:
        """
        Analyze the user prompt and extract structured data.

        Args:
            request: The infographic request

        Returns:
            Extracted data including statistics, sections, etc.
        """
        # Use prompt analyzer for AI-powered extraction
        extraction = await self._prompt_analyzer.analyze(request.topic)

        # Override with explicit request values if provided
        if request.title:
            extraction.title = request.title

        # Merge statistics from request if provided
        if request.statistics:
            for stat_dto in request.statistics:
                from ...infrastructure.ai_providers.prompt_analyzer import StatisticExtraction
                extraction.statistics.append(StatisticExtraction(
                    name=stat_dto.name,
                    value=stat_dto.value,
                    unit=stat_dto.unit,
                    visualization_type=stat_dto.visualization_type,
                    category=stat_dto.category,
                    description=stat_dto.description
                ))

        # Import data from file if path provided
        if request.import_file_path and self._data_importer:
            import_path = Path(request.import_file_path)
            if import_path.exists():
                logger.info(f"Importing data from: {import_path}")
                imported_data = await self._data_importer.import_file(import_path)
                for item in imported_data:
                    from ...infrastructure.ai_providers.prompt_analyzer import StatisticExtraction
                    extraction.statistics.append(StatisticExtraction(
                        name=item.get('name', 'Statistic'),
                        value=float(item.get('value', 0)),
                        unit=item.get('unit', 'units'),
                        visualization_type=item.get('visualization_type', 'bar_chart'),
                        category=item.get('category'),
                        description=item.get('description')
                    ))

        # Update section count from request
        if request.num_sections:
            extraction.num_sections = request.num_sections
            # Ensure we have enough section outlines
            while len(extraction.section_outlines) < extraction.num_sections:
                extraction.section_outlines.append(
                    f"Section {len(extraction.section_outlines) + 1}"
                )

        logger.info(f"Extraction complete:")
        logger.info(f"  - Title: {extraction.title}")
        logger.info(f"  - Word Count: {extraction.word_count}")
        logger.info(f"  - Sections: {extraction.num_sections}")
        logger.info(f"  - Statistics: {len(extraction.statistics)}")
        logger.info(f"  - Image Prompts: {len(extraction.image_prompts)}")

        return extraction

    async def _generate_text_content(
        self,
        extraction: InfographicExtractionResult,
        request: InfographicRequest
    ) -> List[Dict[str, Any]]:
        """
        Generate text content for each section using AI.

        Args:
            extraction: Extracted data from prompt analysis
            request: Original request

        Returns:
            List of section dictionaries with heading and content
        """
        # Format section outlines
        section_outlines_text = "\n".join([
            f"{i+1}. {outline}"
            for i, outline in enumerate(extraction.section_outlines)
        ])

        # Format statistics
        stats_text = "None specified"
        if extraction.statistics:
            stats_text = "\n".join([
                f"- {stat.name}: {stat.value} {stat.unit}"
                for stat in extraction.statistics
            ])

        # Build prompt
        prompt = self.CONTENT_GENERATION_PROMPT.format(
            title=extraction.title,
            topic=extraction.topic,
            word_count=extraction.word_count,
            num_sections=extraction.num_sections,
            tone=extraction.tone,
            section_outlines=section_outlines_text,
            statistics=stats_text
        )

        # Generate content
        logger.info(f"Generating content for {extraction.num_sections} sections...")
        logger.info(f"Target word count: {extraction.word_count}")

        content = await self._text_generator.generate(
            prompt=prompt,
            max_tokens=min(extraction.word_count * 2, 4000),
            temperature=0.7
        )

        # Parse content into sections
        sections = self._parse_content_into_sections(content, extraction)

        # Log word count
        total_words = sum(len(s.get('content', '').split()) for s in sections)
        logger.info(f"Generated {total_words} words across {len(sections)} sections")

        return sections

    def _parse_content_into_sections(
        self,
        content: str,
        extraction: InfographicExtractionResult
    ) -> List[Dict[str, Any]]:
        """
        Parse generated content into sections.

        Args:
            content: Generated text content
            extraction: Extraction result with section outlines

        Returns:
            List of section dictionaries
        """
        sections = []

        # Try to split by section numbers (1., 2., etc.)
        import re

        # Pattern to match section headers like "1. Title" or "1. Title\n"
        section_pattern = r'\n(?=\d+\.\s+[A-Z])'
        parts = re.split(section_pattern, content)

        if len(parts) >= extraction.num_sections:
            # Successfully split into sections
            for i, part in enumerate(parts):
                if i >= extraction.num_sections:
                    break

                # Extract heading and content
                lines = part.strip().split('\n', 1)
                heading = lines[0].strip()

                # Clean up heading (remove leading number if present)
                heading = re.sub(r'^\d+\.\s*', '', heading)

                content_text = lines[1].strip() if len(lines) > 1 else part

                sections.append({
                    'heading': heading or extraction.section_outlines[i],
                    'content': content_text
                })
        else:
            # Couldn't split cleanly, divide content evenly
            words = content.split()
            words_per_section = len(words) // extraction.num_sections

            for i in range(extraction.num_sections):
                start_idx = i * words_per_section
                end_idx = start_idx + words_per_section if i < extraction.num_sections - 1 else len(words)
                section_content = ' '.join(words[start_idx:end_idx])

                sections.append({
                    'heading': extraction.section_outlines[i] if i < len(extraction.section_outlines) else f'Section {i+1}',
                    'content': section_content
                })

        return sections

    async def _generate_visualizations(
        self,
        extraction: InfographicExtractionResult,
        request: InfographicRequest,
        job_id: str
    ) -> List[Path]:
        """
        Generate charts and visualizations for statistics.

        Args:
            extraction: Extracted data with statistics
            request: Original request with color scheme
            job_id: Job identifier for file naming

        Returns:
            List of paths to generated chart images
        """
        charts = []
        colors = request.color_scheme or ['#1e40af', '#3730a3', '#7c3aed']

        # Set colors on visualization engine if supported
        if hasattr(self._visualization_engine, 'set_colors'):
            self._visualization_engine.set_colors(colors)

        chart_dir = self._output_dir / f"charts_{job_id}"
        chart_dir.mkdir(parents=True, exist_ok=True)

        for i, stat in enumerate(extraction.statistics):
            try:
                chart_path = chart_dir / f"chart_{i+1}_{stat.visualization_type}.png"

                logger.info(f"Creating {stat.visualization_type} for: {stat.name}")

                if stat.visualization_type == 'bar_chart':
                    # Create bar chart with the statistic
                    data = {stat.name: stat.value}
                    await self._visualization_engine.create_bar_chart(
                        data=data,
                        title=stat.name,
                        colors=colors,
                        output_path=chart_path
                    )

                elif stat.visualization_type == 'pie_chart':
                    # For pie chart, we need multiple values
                    # Create a simple split if only one value
                    remaining = 100 - stat.value if stat.unit == '%' and stat.value <= 100 else stat.value
                    data = {stat.name: stat.value, 'Other': max(0, remaining)}
                    await self._visualization_engine.create_pie_chart(
                        data=data,
                        title=stat.name,
                        colors=colors,
                        output_path=chart_path
                    )

                elif stat.visualization_type == 'gauge_chart':
                    max_value = 100 if stat.unit == '%' else stat.value * 1.5
                    await self._visualization_engine.create_gauge_chart(
                        value=stat.value,
                        max_value=max_value,
                        title=stat.name,
                        colors=colors,
                        output_path=chart_path
                    )

                elif stat.visualization_type == 'line_chart':
                    # Create simple trend line
                    import random
                    base = stat.value
                    data = {stat.name: [
                        base * (0.8 + random.random() * 0.2),
                        base * (0.85 + random.random() * 0.15),
                        base * (0.9 + random.random() * 0.1),
                        base * (0.95 + random.random() * 0.1),
                        base
                    ]}
                    await self._visualization_engine.create_line_chart(
                        data=data,
                        title=stat.name,
                        colors=colors,
                        output_path=chart_path
                    )

                elif stat.visualization_type == 'number':
                    # Create number display
                    if hasattr(self._visualization_engine, 'create_number_display'):
                        await self._visualization_engine.create_number_display(
                            value=stat.value,
                            label=stat.name,
                            unit=stat.unit,
                            colors=colors,
                            output_path=chart_path
                        )
                    else:
                        # Fallback to gauge
                        await self._visualization_engine.create_gauge_chart(
                            value=stat.value,
                            max_value=stat.value * 1.5,
                            title=stat.name,
                            colors=colors,
                            output_path=chart_path
                        )

                if chart_path.exists():
                    charts.append(chart_path)
                    logger.info(f"  Chart saved: {chart_path.name}")

            except Exception as e:
                logger.error(f"Failed to create chart for {stat.name}: {e}")
                continue

        logger.info(f"Generated {len(charts)} charts")
        return charts

    async def _generate_illustrations(
        self,
        extraction: InfographicExtractionResult,
        request: InfographicRequest,
        job_id: str
    ) -> List[Path]:
        """
        Generate illustrations for document sections.

        Args:
            extraction: Extracted data with image prompts
            request: Original request
            job_id: Job identifier for file naming

        Returns:
            List of paths to generated illustration images
        """
        illustrations = []
        num_images = request.num_images or len(extraction.image_prompts)
        num_images = min(num_images, 4)  # Max 4 images

        image_dir = self._output_dir / f"illustrations_{job_id}"
        image_dir.mkdir(parents=True, exist_ok=True)

        # Get image prompts
        prompts = extraction.image_prompts[:num_images]

        # If not enough prompts, generate more
        while len(prompts) < num_images:
            prompts.append(
                f"Professional infographic illustration about {extraction.topic}, "
                f"clean modern design, suitable for business document"
            )

        # Generate images
        logger.info(f"Generating {len(prompts)} illustrations...")

        for i, prompt in enumerate(prompts):
            try:
                image_path = image_dir / f"illustration_{i+1}.png"

                logger.info(f"  Generating illustration {i+1}: {prompt[:50]}...")

                await self._image_generator.generate_to_file(
                    prompt=prompt,
                    output_path=image_path,
                    width=768,
                    height=512
                )

                if image_path.exists():
                    illustrations.append(image_path)
                    logger.info(f"  Saved: {image_path.name}")

            except Exception as e:
                logger.error(f"Failed to generate illustration {i+1}: {e}")
                continue

        logger.info(f"Generated {len(illustrations)} illustrations")
        return illustrations

    async def _render_document(
        self,
        extraction: InfographicExtractionResult,
        sections: List[Dict[str, Any]],
        charts: List[Path],
        illustrations: List[Path],
        request: InfographicRequest,
        job_id: str
    ) -> Path:
        """
        Render the final PDF document.

        Args:
            extraction: Extracted data
            sections: Generated text sections
            charts: Paths to chart images
            illustrations: Paths to illustration images
            request: Original request
            job_id: Job identifier

        Returns:
            Path to the generated PDF
        """
        # Set up output path
        safe_title = "".join(c if c.isalnum() or c in ' -_' else '_' for c in extraction.title)
        safe_title = safe_title[:50]  # Limit length
        output_filename = f"infographic_{job_id}_{safe_title}.pdf"
        output_path = self._output_dir / output_filename

        # Set colors on renderer
        if request.color_scheme:
            self._document_renderer.set_colors(request.color_scheme)

        # Prepare metadata
        metadata = {
            'author': request.user_id or 'RapidDocs',
            'date': extraction.date,
            'word_count': extraction.word_count
        }

        # Handle logo
        logo_path = None
        if request.logo_path:
            logo_path = Path(request.logo_path)
            if not logo_path.exists():
                logo_path = None

        # Render PDF
        logger.info(f"Rendering PDF: {output_filename}")

        await self._document_renderer.render(
            title=extraction.title,
            sections=sections,
            charts=charts,
            illustrations=illustrations,
            output_path=output_path,
            logo_path=logo_path,
            include_cover=request.include_cover_page,
            metadata=metadata
        )

        return output_path

    def get_status(self) -> Dict[str, Any]:
        """Get use case status information."""
        return {
            "use_case": "GenerateInfographicUseCase",
            "text_generator": {
                "provider": self._text_generator.provider_name,
                "model": self._text_generator.model_name,
                "active": getattr(self._text_generator, 'is_active', True)
            },
            "image_generator": {
                "model": self._image_generator.model_name,
                "active": getattr(self._image_generator, 'is_active', True)
            },
            "visualization_engine": {
                "active": getattr(self._visualization_engine, 'is_active', True)
            },
            "output_directory": str(self._output_dir)
        }
