# CLAUDE.md - RapidDocs Document Generation Platform

## Project Overview

RapidDocs is a professional document generation platform that produces three types of documents:
1. **Invoices** - Business invoices with tables, logos, and AI-generated content
2. **Infographic Documents** - Visual documents with charts, graphs, and AI-generated images
3. **Formal Documents** - Professional text documents with watermarks, redaction, and proper formatting

This specification defines the architecture, implementation guidelines, and standards for the entire codebase.

---

## Architecture Overview

### Clean Architecture Layers
```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                        │
│  (API Routes, Request/Response DTOs, Input Validation)          │
├─────────────────────────────────────────────────────────────────┤
│                        APPLICATION LAYER                         │
│  (Use Cases, Application Services, Orchestrators)               │
├─────────────────────────────────────────────────────────────────┤
│                          DOMAIN LAYER                            │
│  (Entities, Value Objects, Domain Services, Interfaces)         │
├─────────────────────────────────────────────────────────────────┤
│                       INFRASTRUCTURE LAYER                       │
│  (External Services, Repositories, File I/O, AI Providers)      │
└─────────────────────────────────────────────────────────────────┘
```

### Directory Structure
```
rapiddocs/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                          # FastAPI application entry
│   │   ├── config.py                        # Configuration management
│   │   │
│   │   ├── domain/                          # DOMAIN LAYER
│   │   │   ├── __init__.py
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── document.py              # Document entity
│   │   │   │   ├── invoice.py               # Invoice entity
│   │   │   │   ├── user.py                  # User entity
│   │   │   │   └── generation_job.py        # Generation job entity
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── design_spec.py           # Design specification VO
│   │   │   │   ├── statistic.py             # Statistic VO
│   │   │   │   ├── document_format.py       # Output format VO
│   │   │   │   └── watermark_config.py      # Watermark configuration VO
│   │   │   ├── interfaces/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── text_generator.py        # Text generation interface
│   │   │   │   ├── image_generator.py       # Image generation interface
│   │   │   │   ├── document_renderer.py     # Document rendering interface
│   │   │   │   ├── visualization_engine.py  # Chart/graph interface
│   │   │   │   ├── table_generator.py       # Table generation interface
│   │   │   │   ├── watermark_service.py     # Watermark interface
│   │   │   │   ├── redaction_service.py     # Text redaction interface
│   │   │   │   ├── data_importer.py         # CSV/Excel import interface
│   │   │   │   └── document_repository.py   # Document storage interface
│   │   │   └── exceptions.py                # Domain exceptions
│   │   │
│   │   ├── application/                     # APPLICATION LAYER
│   │   │   ├── __init__.py
│   │   │   ├── use_cases/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── generate_invoice.py      # Invoice generation use case
│   │   │   │   ├── generate_infographic.py  # Infographic generation use case
│   │   │   │   ├── generate_formal.py       # Formal doc generation use case
│   │   │   │   ├── import_data.py           # Data import use case
│   │   │   │   └── check_job_status.py      # Job status use case
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── document_orchestrator.py # Orchestrates document generation
│   │   │   │   └── job_manager.py           # Manages generation jobs
│   │   │   └── dto/
│   │   │       ├── __init__.py
│   │   │       ├── invoice_request.py       # Invoice request DTO
│   │   │       ├── infographic_request.py   # Infographic request DTO
│   │   │       ├── formal_request.py        # Formal document request DTO
│   │   │       └── generation_response.py   # Response DTOs
│   │   │
│   │   ├── infrastructure/                  # INFRASTRUCTURE LAYER
│   │   │   ├── __init__.py
│   │   │   ├── ai_providers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_text_generator.py   # Base text generator
│   │   │   │   ├── gemini_text_generator.py # Gemini 3 Pro implementation
│   │   │   │   ├── base_image_generator.py  # Base image generator
│   │   │   │   └── banana_image_generator.py# Nano Banana implementation
│   │   │   ├── document_renderers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_renderer.py         # Base document renderer
│   │   │   │   ├── pdf_renderer.py          # PDF output (ReportLab)
│   │   │   │   ├── docx_renderer.py         # DOCX output (python-docx)
│   │   │   │   ├── html_renderer.py         # HTML output
│   │   │   │   └── markdown_renderer.py     # Markdown output
│   │   │   ├── visualization/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── matplotlib_engine.py     # Matplotlib implementation
│   │   │   │   └── chart_types.py           # Chart type definitions
│   │   │   ├── tables/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── reportlab_tables.py      # ReportLab table implementation
│   │   │   │   └── table_styles.py          # Table styling definitions
│   │   │   ├── watermark/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pypdf2_watermark.py      # PyPDF2 watermark implementation
│   │   │   │   └── watermark_types.py       # Image/text watermark types
│   │   │   ├── redaction/
│   │   │   │   ├── __init__.py
│   │   │   │   └── text_redactor.py         # Text redaction implementation
│   │   │   ├── data_import/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── csv_importer.py          # CSV import implementation
│   │   │   │   └── excel_importer.py        # Excel import implementation
│   │   │   ├── storage/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── file_storage.py          # Local file storage
│   │   │   │   └── logo_processor.py        # Logo processing (SVG→PNG)
│   │   │   ├── persistence/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── mongodb_repository.py    # MongoDB implementation
│   │   │   │   └── database.py              # Database connection
│   │   │   └── external/
│   │   │       ├── __init__.py
│   │   │       └── huggingface_client.py    # HuggingFace API client
│   │   │
│   │   ├── presentation/                    # PRESENTATION LAYER
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── invoice_routes.py        # Invoice API endpoints
│   │   │   │   ├── infographic_routes.py    # Infographic API endpoints
│   │   │   │   ├── formal_routes.py         # Formal document endpoints
│   │   │   │   ├── job_routes.py            # Job status endpoints
│   │   │   │   ├── upload_routes.py         # File upload endpoints
│   │   │   │   └── auth_routes.py           # Authentication endpoints
│   │   │   ├── schemas/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── invoice_schemas.py       # Invoice Pydantic schemas
│   │   │   │   ├── infographic_schemas.py   # Infographic Pydantic schemas
│   │   │   │   ├── formal_schemas.py        # Formal document schemas
│   │   │   │   ├── common_schemas.py        # Shared schemas
│   │   │   │   └── auth_schemas.py          # Auth schemas
│   │   │   └── middleware/
│   │   │       ├── __init__.py
│   │   │       └── error_handler.py         # Global error handling
│   │   │
│   │   └── shared/                          # SHARED UTILITIES
│   │       ├── __init__.py
│   │       ├── logger.py                    # Logging configuration
│   │       ├── constants.py                 # Application constants
│   │       └── utils.py                     # Helper utilities
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── unit/
│   │   │   ├── domain/
│   │   │   ├── application/
│   │   │   └── infrastructure/
│   │   └── integration/
│   │       └── api/
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── ts/
│   │   │   ├── main.ts
│   │   │   ├── api/
│   │   │   │   ├── client.ts
│   │   │   │   └── endpoints.ts
│   │   │   ├── components/
│   │   │   │   ├── InvoiceForm.ts
│   │   │   │   ├── InfographicForm.ts
│   │   │   │   ├── FormalDocumentForm.ts
│   │   │   │   ├── ColorPalette.ts
│   │   │   │   ├── StatisticsForm.ts
│   │   │   │   ├── DataImport.ts
│   │   │   │   └── FormatSelector.ts
│   │   │   ├── types/
│   │   │   │   ├── invoice.ts
│   │   │   │   ├── infographic.ts
│   │   │   │   ├── formal.ts
│   │   │   │   └── common.ts
│   │   │   └── utils/
│   │   │       └── validation.ts
│   │   └── styles/
│   │       └── main.css
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── .gitignore
├── docker-compose.yml
└── CLAUDE.md                                # This file
```

---

## Domain Layer Specifications

### Domain Interfaces (Contracts)

All infrastructure implementations MUST implement these interfaces to ensure loose coupling.

#### Text Generator Interface
```python
# backend/app/domain/interfaces/text_generator.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ITextGenerator(ABC):
    """
    Interface for text generation providers.
    Implementations: Gemini 3 Pro, OpenAI, Anthropic, Local LLM
    """
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate text based on prompt and parameters."""
        pass
    
    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        output_schema: Dict[str, Any],
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """Generate structured output matching schema."""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model identifier."""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass
```

#### Image Generator Interface
```python
# backend/app/domain/interfaces/image_generator.py

from abc import ABC, abstractmethod
from typing import Optional, List
from pathlib import Path

class IImageGenerator(ABC):
    """
    Interface for image generation providers.
    Implementations: Nano Banana, FLUX, Stable Diffusion, DALL-E
    """
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        style_hints: Optional[str] = None
    ) -> bytes:
        """Generate image and return as bytes."""
        pass
    
    @abstractmethod
    async def generate_batch(
        self,
        prompts: List[str],
        width: int = 512,
        height: int = 512
    ) -> List[bytes]:
        """Generate multiple images."""
        pass
    
    @abstractmethod
    async def generate_to_file(
        self,
        prompt: str,
        output_path: Path,
        width: int = 512,
        height: int = 512
    ) -> Path:
        """Generate image and save to file."""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model identifier."""
        pass
```

#### Document Renderer Interface
```python
# backend/app/domain/interfaces/document_renderer.py

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pathlib import Path
from ..value_objects.document_format import DocumentFormat

class IDocumentRenderer(ABC):
    """
    Interface for document rendering.
    Implementations: PDF (ReportLab), DOCX (python-docx), HTML, Markdown
    """
    
    @abstractmethod
    async def render(
        self,
        content: Dict[str, Any],
        output_path: Path,
        format: DocumentFormat
    ) -> Path:
        """Render document to specified format."""
        pass
    
    @abstractmethod
    def add_text(self, text: str, style: Optional[Dict] = None) -> None:
        """Add text content to document."""
        pass
    
    @abstractmethod
    def add_image(
        self,
        image_path: Path,
        width: Optional[float] = None,
        height: Optional[float] = None,
        caption: Optional[str] = None
    ) -> None:
        """Add image to document."""
        pass
    
    @abstractmethod
    def add_table(
        self,
        data: List[List[Any]],
        headers: Optional[List[str]] = None,
        style: Optional[Dict] = None
    ) -> None:
        """Add table to document."""
        pass
    
    @abstractmethod
    def add_page_break(self) -> None:
        """Add page break."""
        pass
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[DocumentFormat]:
        """Return list of supported output formats."""
        pass
```

#### Visualization Engine Interface
```python
# backend/app/domain/interfaces/visualization_engine.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

class IVisualizationEngine(ABC):
    """
    Interface for chart/graph generation.
    Implementations: Matplotlib, Plotly, Chart.js backend
    """
    
    @abstractmethod
    async def create_bar_chart(
        self,
        data: Dict[str, float],
        title: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """Create bar chart."""
        pass
    
    @abstractmethod
    async def create_line_chart(
        self,
        data: Dict[str, List[float]],
        title: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """Create line chart."""
        pass
    
    @abstractmethod
    async def create_pie_chart(
        self,
        data: Dict[str, float],
        title: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """Create pie chart."""
        pass
    
    @abstractmethod
    async def create_gauge_chart(
        self,
        value: float,
        max_value: float,
        title: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """Create gauge chart."""
        pass
```

#### Table Generator Interface
```python
# backend/app/domain/interfaces/table_generator.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class ITableGenerator(ABC):
    """
    Interface for table generation (primarily for invoices).
    Implementations: ReportLab tables, HTML tables, Markdown tables
    """
    
    @abstractmethod
    def create_invoice_table(
        self,
        line_items: List[Dict[str, Any]],
        columns: List[str],
        style: Optional[Dict] = None
    ) -> Any:
        """Create invoice line items table."""
        pass
    
    @abstractmethod
    def create_summary_table(
        self,
        subtotal: float,
        tax: float,
        total: float,
        currency: str = "USD"
    ) -> Any:
        """Create invoice summary table."""
        pass
    
    @abstractmethod
    def set_column_widths(self, widths: List[float]) -> None:
        """Set column widths."""
        pass
    
    @abstractmethod
    def apply_style(self, style_config: Dict[str, Any]) -> None:
        """Apply styling to table."""
        pass
```

#### Watermark Service Interface
```python
# backend/app/domain/interfaces/watermark_service.py

from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path
from ..value_objects.watermark_config import WatermarkConfig

class IWatermarkService(ABC):
    """
    Interface for watermark operations.
    Implementations: PyPDF2 watermark, ReportLab overlay
    """
    
    @abstractmethod
    async def add_image_watermark(
        self,
        input_pdf: Path,
        output_pdf: Path,
        image_path: Path,
        config: WatermarkConfig
    ) -> Path:
        """Add image watermark to PDF."""
        pass
    
    @abstractmethod
    async def add_text_watermark(
        self,
        input_pdf: Path,
        output_pdf: Path,
        text: str,
        config: WatermarkConfig
    ) -> Path:
        """Add text watermark to PDF."""
        pass
    
    @abstractmethod
    async def create_watermark_page(
        self,
        content: Any,
        page_width: float,
        page_height: float,
        opacity: float
    ) -> bytes:
        """Create a watermark page overlay."""
        pass
```

#### Redaction Service Interface
```python
# backend/app/domain/interfaces/redaction_service.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class IRedactionService(ABC):
    """
    Interface for text redaction operations.
    Implementations: Regex-based redaction, AI-based PII detection
    """
    
    @abstractmethod
    def redact_patterns(
        self,
        text: str,
        patterns: List[str],
        replacement: str = "[REDACTED]"
    ) -> str:
        """Redact text matching regex patterns."""
        pass
    
    @abstractmethod
    def redact_pii(
        self,
        text: str,
        pii_types: List[str]
    ) -> str:
        """Redact personally identifiable information."""
        pass
    
    @abstractmethod
    def redact_custom(
        self,
        text: str,
        redaction_rules: List[Dict[str, Any]]
    ) -> str:
        """Apply custom redaction rules."""
        pass
    
    @property
    @abstractmethod
    def supported_pii_types(self) -> List[str]:
        """Return list of supported PII types for redaction."""
        pass
```

#### Data Importer Interface
```python
# backend/app/domain/interfaces/data_importer.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

class IDataImporter(ABC):
    """
    Interface for importing data from external files.
    Implementations: CSV importer, Excel importer
    """
    
    @abstractmethod
    async def import_file(
        self,
        file_path: Path,
        options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Import data from file."""
        pass
    
    @abstractmethod
    async def validate_file(
        self,
        file_path: Path,
        expected_columns: Optional[List[str]] = None
    ) -> bool:
        """Validate file format and structure."""
        pass
    
    @abstractmethod
    def preview(
        self,
        file_path: Path,
        rows: int = 5
    ) -> List[Dict[str, Any]]:
        """Preview first N rows of data."""
        pass
    
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        pass
```

---

## Value Objects

### Document Format Value Object
```python
# backend/app/domain/value_objects/document_format.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional

class OutputFormat(Enum):
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    MARKDOWN = "md"
    RTF = "rtf"
    
@dataclass(frozen=True)
class DocumentFormat:
    format: OutputFormat
    dpi: int = 300
    compression: bool = True
    embed_fonts: bool = True
    
    @classmethod
    def pdf(cls, dpi: int = 300) -> "DocumentFormat":
        return cls(format=OutputFormat.PDF, dpi=dpi)
    
    @classmethod
    def docx(cls) -> "DocumentFormat":
        return cls(format=OutputFormat.DOCX)
    
    @classmethod
    def html(cls) -> "DocumentFormat":
        return cls(format=OutputFormat.HTML)
    
    @classmethod
    def markdown(cls) -> "DocumentFormat":
        return cls(format=OutputFormat.MARKDOWN)
```

### Watermark Configuration Value Object
```python
# backend/app/domain/value_objects/watermark_config.py

from dataclasses import dataclass
from typing import Optional
from enum import Enum

class WatermarkPosition(Enum):
    CENTER = "center"
    DIAGONAL = "diagonal"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"

class WatermarkType(Enum):
    IMAGE = "image"
    TEXT = "text"

@dataclass(frozen=True)
class WatermarkConfig:
    watermark_type: WatermarkType
    opacity: float = 0.15
    position: WatermarkPosition = WatermarkPosition.CENTER
    size_inches: float = 3.0
    skip_first_page: bool = True
    rotation: float = 0.0  # For diagonal text watermarks
    font_size: int = 48    # For text watermarks
    font_color: str = "#000000"  # For text watermarks
```

---

## Application Layer Use Cases

### Invoice Generation Use Case
```python
# backend/app/application/use_cases/generate_invoice.py

from typing import Optional
from pathlib import Path
from ..dto.invoice_request import InvoiceRequest
from ...domain.interfaces.text_generator import ITextGenerator
from ...domain.interfaces.image_generator import IImageGenerator
from ...domain.interfaces.document_renderer import IDocumentRenderer
from ...domain.interfaces.table_generator import ITableGenerator
from ...domain.interfaces.data_importer import IDataImporter

class GenerateInvoiceUseCase:
    """
    Use case for generating invoice documents.
    
    Components:
    - Text Generator: Generates invoice descriptions, notes, terms
    - Image Generator: Generates/processes business logo
    - Table Generator: Creates line items and summary tables
    - Document Renderer: Outputs final document in specified format
    - Data Importer: (Optional) Imports line items from CSV/Excel
    """
    
    def __init__(
        self,
        text_generator: ITextGenerator,
        image_generator: IImageGenerator,
        document_renderer: IDocumentRenderer,
        table_generator: ITableGenerator,
        data_importer: Optional[IDataImporter] = None
    ):
        self._text_generator = text_generator
        self._image_generator = image_generator
        self._document_renderer = document_renderer
        self._table_generator = table_generator
        self._data_importer = data_importer
    
    async def execute(self, request: InvoiceRequest) -> Path:
        """Execute invoice generation."""
        # Implementation details...
        pass
```

### Infographic Document Generation Use Case
```python
# backend/app/application/use_cases/generate_infographic.py

from typing import Optional, List
from pathlib import Path
from ..dto.infographic_request import InfographicRequest
from ...domain.interfaces.text_generator import ITextGenerator
from ...domain.interfaces.image_generator import IImageGenerator
from ...domain.interfaces.document_renderer import IDocumentRenderer
from ...domain.interfaces.visualization_engine import IVisualizationEngine
from ...domain.interfaces.data_importer import IDataImporter

class GenerateInfographicUseCase:
    """
    Use case for generating infographic documents.
    
    Components:
    - Text Generator: Generates document text content
    - Image Generator: Generates contextual images and logo
    - Visualization Engine: Creates charts and graphs from statistics
    - Document Renderer: Outputs final document in specified format
    - Data Importer: (Optional) Imports statistics from CSV/Excel
    """
    
    def __init__(
        self,
        text_generator: ITextGenerator,
        image_generator: IImageGenerator,
        document_renderer: IDocumentRenderer,
        visualization_engine: IVisualizationEngine,
        data_importer: Optional[IDataImporter] = None
    ):
        self._text_generator = text_generator
        self._image_generator = image_generator
        self._document_renderer = document_renderer
        self._visualization_engine = visualization_engine
        self._data_importer = data_importer
    
    async def execute(self, request: InfographicRequest) -> Path:
        """Execute infographic document generation."""
        # Implementation details...
        pass
```

### Formal Document Generation Use Case
```python
# backend/app/application/use_cases/generate_formal.py

from typing import Optional
from pathlib import Path
from ..dto.formal_request import FormalRequest
from ...domain.interfaces.text_generator import ITextGenerator
from ...domain.interfaces.image_generator import IImageGenerator
from ...domain.interfaces.document_renderer import IDocumentRenderer
from ...domain.interfaces.watermark_service import IWatermarkService
from ...domain.interfaces.redaction_service import IRedactionService
from ...domain.interfaces.data_importer import IDataImporter

class GenerateFormalDocumentUseCase:
    """
    Use case for generating formal documents.
    
    Components:
    - Text Generator: Generates formal document text content
    - Image Generator: Generates/processes business logo
    - Document Renderer: Outputs formatted document
    - Watermark Service: Adds image/text watermarks
    - Redaction Service: Redacts sensitive information
    - Data Importer: (Optional) Imports data from CSV/Excel
    """
    
    def __init__(
        self,
        text_generator: ITextGenerator,
        image_generator: IImageGenerator,
        document_renderer: IDocumentRenderer,
        watermark_service: IWatermarkService,
        redaction_service: IRedactionService,
        data_importer: Optional[IDataImporter] = None
    ):
        self._text_generator = text_generator
        self._image_generator = image_generator
        self._document_renderer = document_renderer
        self._watermark_service = watermark_service
        self._redaction_service = redaction_service
        self._data_importer = data_importer
    
    async def execute(self, request: FormalRequest) -> Path:
        """Execute formal document generation."""
        # Implementation details...
        pass
```

---

## Infrastructure Implementations

### AI Provider Implementations

#### Gemini 3 Pro Text Generator
```python
# backend/app/infrastructure/ai_providers/gemini_text_generator.py

"""
Gemini 3 Pro text generation implementation.

Required Environment Variables:
- GEMINI_API_KEY: Google AI API key

Dependencies:
- google-generativeai>=0.5.0
"""

from typing import Dict, Any, Optional
from ...domain.interfaces.text_generator import ITextGenerator

class GeminiTextGenerator(ITextGenerator):
    """
    Gemini 3 Pro implementation of text generation.
    
    Features:
    - Structured output generation
    - Context-aware prompting
    - Rate limiting and retry logic
    """
    
    def __init__(self, api_key: str, model: str = "gemini-3-pro"):
        self._api_key = api_key
        self._model = model
        # Initialize client...
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        # Implementation...
        pass
    
    @property
    def model_name(self) -> str:
        return self._model
    
    @property
    def provider_name(self) -> str:
        return "Google Gemini"
```

#### Nano Banana Image Generator
```python
# backend/app/infrastructure/ai_providers/banana_image_generator.py

"""
Nano Banana image generation implementation.

Required Environment Variables:
- BANANA_API_KEY: Banana ML API key

Dependencies:
- banana-dev>=0.4.0
"""

from typing import Optional, List
from pathlib import Path
from ...domain.interfaces.image_generator import IImageGenerator

class BananaImageGenerator(IImageGenerator):
    """
    Nano Banana implementation of image generation.
    
    Features:
    - Fast inference
    - Style-guided generation
    - Batch processing
    """
    
    def __init__(self, api_key: str, model: str = "nano-banana"):
        self._api_key = api_key
        self._model = model
        # Initialize client...
    
    async def generate(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        style_hints: Optional[str] = None
    ) -> bytes:
        # Implementation...
        pass
    
    @property
    def model_name(self) -> str:
        return self._model
```

### Provider Factory (Dependency Injection)
```python
# backend/app/infrastructure/ai_providers/__init__.py

from typing import Type
from ...domain.interfaces.text_generator import ITextGenerator
from ...domain.interfaces.image_generator import IImageGenerator
from .gemini_text_generator import GeminiTextGenerator
from .banana_image_generator import BananaImageGenerator

class AIProviderFactory:
    """
    Factory for creating AI provider instances.
    Allows easy swapping of implementations.
    """
    
    _text_generators: dict = {
        "gemini": GeminiTextGenerator,
        # Add more providers here:
        # "openai": OpenAITextGenerator,
        # "anthropic": AnthropicTextGenerator,
    }
    
    _image_generators: dict = {
        "banana": BananaImageGenerator,
        # Add more providers here:
        # "flux": FluxImageGenerator,
        # "dalle": DalleImageGenerator,
    }
    
    @classmethod
    def get_text_generator(cls, provider: str, **kwargs) -> ITextGenerator:
        """Get text generator by provider name."""
        generator_class = cls._text_generators.get(provider)
        if not generator_class:
            raise ValueError(f"Unknown text generator provider: {provider}")
        return generator_class(**kwargs)
    
    @classmethod
    def get_image_generator(cls, provider: str, **kwargs) -> IImageGenerator:
        """Get image generator by provider name."""
        generator_class = cls._image_generators.get(provider)
        if not generator_class:
            raise ValueError(f"Unknown image generator provider: {provider}")
        return generator_class(**kwargs)
    
    @classmethod
    def register_text_generator(
        cls,
        name: str,
        generator_class: Type[ITextGenerator]
    ) -> None:
        """Register a new text generator provider."""
        cls._text_generators[name] = generator_class
    
    @classmethod
    def register_image_generator(
        cls,
        name: str,
        generator_class: Type[IImageGenerator]
    ) -> None:
        """Register a new image generator provider."""
        cls._image_generators[name] = generator_class
```

---

## Document Type Specifications

### Invoice Document

**Components:**
1. **Header Section**
   - Business logo (top-left or top-right)
   - Company name and address
   - Invoice number and date

2. **Client Information**
   - Client name
   - Client address
   - Client contact details

3. **Line Items Table**
   - Item description
   - Quantity
   - Unit price
   - Total
   - Created using `ITableGenerator` interface

4. **Summary Section**
   - Subtotal
   - Tax (with rate)
   - Total due
   - Currency indicator

5. **Footer Section**
   - Payment terms (AI-generated)
   - Notes (AI-generated)
   - Bank details

**Data Import Support:**
- CSV columns: `item,description,quantity,unit_price`
- Excel sheets: Same structure, supports multiple sheets

### Infographic Document

**Components:**
1. **Cover Page**
   - Title
   - Business logo
   - Color theme accent
   - Date

2. **Text Content**
   - AI-generated sections
   - Headings with color theme
   - Professional formatting

3. **Visualizations**
   - Bar charts
   - Line charts
   - Pie charts
   - Gauge charts
   - Created using `IVisualizationEngine` interface

4. **AI-Generated Images**
   - 2-4 contextual images
   - Theme-matched colors
   - Created using `IImageGenerator` interface

5. **Statistics Integration**
   - Statistics mentioned in text
   - Each statistic has corresponding visualization

**Data Import Support:**
- CSV columns: `name,value,unit,visualization_type`
- Excel sheets: Same structure, supports multiple sheets

### Formal Document

**Components:**
1. **Cover Page**
   - Title
   - Business logo
   - Author/Company name
   - Date

2. **Text Content**
   - AI-generated formal text
   - Proper heading hierarchy
   - Professional formatting
   - No images or charts

3. **Edge Decorations** (Optional)
   - 3 vertical lines on right edge
   - Alternating theme colors
   - Varying thickness

4. **Watermark** (Optional)
   - Image watermark (logo)
   - Text watermark (custom text)
   - Configurable opacity and position
   - Implemented via `IWatermarkService` interface

5. **Redaction** (New Feature)
   - Pattern-based redaction
   - PII detection and redaction
   - Custom redaction rules
   - Implemented via `IRedactionService` interface

**Data Import Support:**
- CSV: Structured data for document sections
- Excel: Same structure, supports multiple sheets

---

## Output Format Support

### Supported Formats

| Format | Extension | Renderer | Features |
|--------|-----------|----------|----------|
| PDF | .pdf | ReportLab | Full feature support |
| DOCX | .docx | python-docx | Text, tables, images |
| HTML | .html | Jinja2 templates | Web-ready output |
| Markdown | .md | Python strings | Plain text with formatting |

### Format Selection

Users can specify output format via:
- API parameter: `output_format: "pdf" | "docx" | "html" | "md"`
- Frontend dropdown selector
- Default: PDF

---

## Data Import Feature

### Supported File Types

1. **CSV Files**
   - Standard comma-separated values
   - UTF-8 encoding
   - Header row required

2. **Excel Files**
   - .xlsx format
   - .xls format (legacy)
   - Multiple sheet support

### Import Workflow
```
1. User uploads CSV/Excel file
2. System validates file structure
3. System previews first N rows
4. User confirms/maps columns
5. Data integrated into document generation
```

### Column Mapping

For each document type, expected columns:

**Invoice:**
```
item, description, quantity, unit_price, tax_rate (optional)
```

**Infographic:**
```
name, value, unit, visualization_type, category (optional)
```

**Formal Document:**
```
section, content, priority (optional)
```

---

## API Endpoints

### Invoice Endpoints
```
POST /api/v1/invoice/generate
GET  /api/v1/invoice/status/{job_id}
GET  /api/v1/invoice/download/{job_id}
POST /api/v1/invoice/import-data
```

### Infographic Endpoints
```
POST /api/v1/infographic/generate
GET  /api/v1/infographic/status/{job_id}
GET  /api/v1/infographic/download/{job_id}
POST /api/v1/infographic/import-data
```

### Formal Document Endpoints
```
POST /api/v1/formal/generate
GET  /api/v1/formal/status/{job_id}
GET  /api/v1/formal/download/{job_id}
POST /api/v1/formal/import-data
```

### Common Endpoints
```
POST /api/v1/upload/logo
POST /api/v1/upload/data
GET  /api/v1/formats/supported
```

---

## Configuration

### Environment Variables
```bash
# Application
APP_NAME=RapidDocs
APP_ENV=development|production
DEBUG=True|False
API_PREFIX=/api/v1

# Database
MONGODB_URL=mongodb+srv://...
MONGODB_DB_NAME=rapiddocs

# AI Providers
TEXT_GENERATOR_PROVIDER=gemini
TEXT_GENERATOR_API_KEY=xxx
TEXT_GENERATOR_MODEL=gemini-3-pro

IMAGE_GENERATOR_PROVIDER=banana
IMAGE_GENERATOR_API_KEY=xxx
IMAGE_GENERATOR_MODEL=nano-banana

# File Storage
UPLOAD_DIR=./uploads
OUTPUT_DIR=./generated
MAX_UPLOAD_SIZE=10485760

# Security
JWT_SECRET_KEY=xxx
JWT_REFRESH_SECRET_KEY=xxx
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---

## Dependency Injection Setup
```python
# backend/app/main.py

from fastapi import FastAPI
from .infrastructure.ai_providers import AIProviderFactory
from .infrastructure.document_renderers import DocumentRendererFactory
from .infrastructure.visualization import MatplotlibEngine
from .infrastructure.tables import ReportLabTableGenerator
from .infrastructure.watermark import PyPDF2WatermarkService
from .infrastructure.redaction import RegexRedactionService
from .infrastructure.data_import import CSVImporter, ExcelImporter
from .application.use_cases.generate_invoice import GenerateInvoiceUseCase
from .application.use_cases.generate_infographic import GenerateInfographicUseCase
from .application.use_cases.generate_formal import GenerateFormalDocumentUseCase
from .config import settings

def create_app() -> FastAPI:
    app = FastAPI(title="RapidDocs API")
    
    # Create AI providers
    text_generator = AIProviderFactory.get_text_generator(
        provider=settings.TEXT_GENERATOR_PROVIDER,
        api_key=settings.TEXT_GENERATOR_API_KEY,
        model=settings.TEXT_GENERATOR_MODEL
    )
    
    image_generator = AIProviderFactory.get_image_generator(
        provider=settings.IMAGE_GENERATOR_PROVIDER,
        api_key=settings.IMAGE_GENERATOR_API_KEY,
        model=settings.IMAGE_GENERATOR_MODEL
    )
    
    # Create infrastructure services
    pdf_renderer = DocumentRendererFactory.get_renderer("pdf")
    visualization_engine = MatplotlibEngine()
    table_generator = ReportLabTableGenerator()
    watermark_service = PyPDF2WatermarkService()
    redaction_service = RegexRedactionService()
    csv_importer = CSVImporter()
    excel_importer = ExcelImporter()
    
    # Create use cases
    invoice_use_case = GenerateInvoiceUseCase(
        text_generator=text_generator,
        image_generator=image_generator,
        document_renderer=pdf_renderer,
        table_generator=table_generator,
        data_importer=csv_importer
    )
    
    infographic_use_case = GenerateInfographicUseCase(
        text_generator=text_generator,
        image_generator=image_generator,
        document_renderer=pdf_renderer,
        visualization_engine=visualization_engine,
        data_importer=excel_importer
    )
    
    formal_use_case = GenerateFormalDocumentUseCase(
        text_generator=text_generator,
        image_generator=image_generator,
        document_renderer=pdf_renderer,
        watermark_service=watermark_service,
        redaction_service=redaction_service,
        data_importer=csv_importer
    )
    
    # Store in app state for route access
    app.state.invoice_use_case = invoice_use_case
    app.state.infographic_use_case = infographic_use_case
    app.state.formal_use_case = formal_use_case
    
    return app
```

---

## Testing Guidelines

### Unit Tests

- Test each domain interface implementation independently
- Mock external dependencies (AI providers, file system)
- Test value objects for immutability and validation

### Integration Tests

- Test complete use case flows
- Use test databases
- Mock AI providers with deterministic responses

### Test File Structure
```
tests/
├── unit/
│   ├── domain/
│   │   ├── test_entities.py
│   │   └── test_value_objects.py
│   ├── application/
│   │   └── test_use_cases.py
│   └── infrastructure/
│       ├── test_text_generators.py
│       ├── test_image_generators.py
│       ├── test_renderers.py
│       └── test_importers.py
└── integration/
    └── api/
        ├── test_invoice_endpoints.py
        ├── test_infographic_endpoints.py
        └── test_formal_endpoints.py
```

---

## Code Standards

### Python Standards

1. **Type Hints**: All functions must have type hints
2. **Docstrings**: All public classes and methods must have docstrings
3. **Async**: All I/O operations must be async
4. **Error Handling**: Use domain-specific exceptions
5. **Logging**: Use structured logging via `shared/logger.py`

### TypeScript Standards

1. **Types**: No `any` types except where absolutely necessary
2. **Interfaces**: Define interfaces for all API responses
3. **Components**: One component per file
4. **Error Handling**: Use try-catch with proper error types

### Git Commit Standards
```
feat: Add new feature
fix: Bug fix
refactor: Code refactoring
docs: Documentation changes
test: Test additions/changes
chore: Maintenance tasks
```

---

## Future Change Guidelines

**IMPORTANT: All future modifications to this codebase MUST adhere to the following:**

1. **Interface Compliance**
   - Any new service implementation MUST implement the corresponding domain interface
   - Never bypass interfaces for "quick fixes"

2. **Dependency Injection**
   - All dependencies MUST be injected via constructors
   - Never instantiate dependencies inside classes
   - Use the factory pattern for creating implementations

3. **Separation of Concerns**
   - Domain layer: No external dependencies
   - Application layer: Only domain interfaces
   - Infrastructure layer: Concrete implementations
   - Presentation layer: HTTP concerns only

4. **Adding New Providers**
   - Create implementation class in `infrastructure/`
   - Register in corresponding factory
   - Update environment variables documentation
   - Add unit tests for new implementation

5. **Adding New Features**
   - Define interface in `domain/interfaces/` first
   - Create implementation in `infrastructure/`
   - Update use cases in `application/use_cases/`
   - Add API endpoints in `presentation/routes/`

6. **Documentation**
   - Update this CLAUDE.md file for architectural changes
   - Add inline documentation for complex logic
   - Update API documentation (OpenAPI/Swagger)

7. **Testing**
   - All new code must have unit tests
   - Integration tests for API changes
   - Mock external services appropriately

8. **No Markdown Files**
   - Do not create additional .md files for documentation
   - All documentation lives in this CLAUDE.md file
   - Code comments for implementation details

---

## Migration Checklist

To migrate from the current codebase to this architecture:

- [ ] Create new directory structure
- [ ] Define all domain interfaces
- [ ] Create value objects
- [ ] Implement infrastructure services
- [ ] Create use cases
- [ ] Update API routes
- [ ] Migrate frontend to new API structure
- [ ] Remove old/unused files
- [ ] Remove all existing .md files (except this one)
- [ ] Update dependencies in requirements.txt
- [ ] Update environment variables
- [ ] Create comprehensive tests
- [ ] Update Dockerfile
- [ ] Update docker-compose.yml

---

## Dependencies

### Backend Dependencies
```txt
# Core
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.10.0
pydantic-settings>=2.7.0
python-dotenv>=1.0.0

# Database
motor>=3.3.0
pymongo[srv]>=4.6.0

# AI Providers
google-generativeai>=0.5.0
banana-dev>=0.4.0

# Document Generation
reportlab>=4.0.0
python-docx>=1.1.0
PyPDF2>=3.0.0
Pillow>=10.0.0

# Visualization
matplotlib>=3.8.0

# Data Import
pandas>=2.0.0
openpyxl>=3.1.0

# Image Processing
cairosvg>=2.8.0

# Security
python-jose[cryptography]>=3.3.0
bcrypt>=4.0.0

# Utilities
aiofiles>=23.2.0
python-multipart>=0.0.6
httpx>=0.27.0
```

### Frontend Dependencies
```json
{
  "dependencies": {
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0"
  }
}
```

---

**Version**: 2.0.0  
**Last Updated**: January 2025  
**Maintained By**: Development Team

**This is the single source of truth for the RapidDocs codebase architecture and standards.**