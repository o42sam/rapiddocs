"""
Formal Document Request DTO.
Data transfer object for formal document generation requests.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class RedactionRule:
    """DTO for redaction rules."""
    pattern: str
    replacement: str = "[REDACTED]"
    rule_type: str = "regex"  # regex, pii


@dataclass
class FormalRequest:
    """
    DTO for formal document generation request.

    Attributes:
        title: Document title
        topic: Main topic for content generation
        sections: Number of sections to generate
        words_per_section: Approximate words per section
        tone: Writing tone (professional, academic, legal, business)
        include_edge_decorations: Whether to include edge decorations
        watermark_type: Type of watermark (none, image, text)
        watermark_text: Text for text watermark
        watermark_image_path: Path to image for image watermark
        watermark_opacity: Watermark opacity (0.0-1.0)
        redaction_enabled: Whether to apply redaction
        redaction_rules: List of redaction rules
        pii_types_to_redact: List of PII types to redact
        color_scheme: List of hex color codes
        logo_path: Optional path to logo file
        output_format: Output format (pdf, docx, html, md)
        import_file_path: Optional path to CSV/Excel for data
        user_id: ID of requesting user
    """
    title: str
    topic: str
    sections: int = 3
    words_per_section: int = 300
    tone: str = "professional"
    include_edge_decorations: bool = False
    watermark_type: str = "none"  # none, image, text
    watermark_text: Optional[str] = None
    watermark_image_path: Optional[str] = None
    watermark_opacity: float = 0.15
    redaction_enabled: bool = False
    redaction_rules: List[RedactionRule] = None
    pii_types_to_redact: List[str] = None
    color_scheme: List[str] = None
    logo_path: Optional[str] = None
    output_format: str = "pdf"
    import_file_path: Optional[str] = None
    user_id: Optional[str] = None

    def __post_init__(self):
        """Set defaults."""
        if self.color_scheme is None:
            self.color_scheme = ["#1e40af", "#3730a3", "#7c3aed"]
        if self.redaction_rules is None:
            self.redaction_rules = []
        if self.pii_types_to_redact is None:
            self.pii_types_to_redact = []

    def validate(self) -> List[str]:
        """
        Validate the request.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not self.title:
            errors.append("Title is required")
        if not self.topic:
            errors.append("Topic is required")

        if self.sections < 1:
            errors.append("Number of sections must be at least 1")
        if self.words_per_section < 50:
            errors.append("Words per section must be at least 50")

        valid_tones = ["professional", "academic", "legal", "business"]
        if self.tone not in valid_tones:
            errors.append(f"Invalid tone. Must be one of: {', '.join(valid_tones)}")

        valid_watermark_types = ["none", "image", "text"]
        if self.watermark_type not in valid_watermark_types:
            errors.append(f"Invalid watermark type. Must be one of: {', '.join(valid_watermark_types)}")

        if self.watermark_type == "text" and not self.watermark_text:
            errors.append("Watermark text is required for text watermark")
        if self.watermark_type == "image" and not self.watermark_image_path:
            errors.append("Watermark image path is required for image watermark")

        if not 0.0 <= self.watermark_opacity <= 1.0:
            errors.append("Watermark opacity must be between 0.0 and 1.0")

        valid_formats = ["pdf", "docx", "html", "md"]
        if self.output_format not in valid_formats:
            errors.append(f"Invalid output format. Must be one of: {', '.join(valid_formats)}")

        for color in self.color_scheme:
            if not color.startswith("#") or len(color) != 7:
                errors.append(f"Invalid color code: {color}")

        valid_pii_types = ["email", "phone", "ssn", "credit_card", "address"]
        for pii_type in self.pii_types_to_redact:
            if pii_type not in valid_pii_types:
                errors.append(f"Invalid PII type: {pii_type}. Must be one of: {', '.join(valid_pii_types)}")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "topic": self.topic,
            "sections": self.sections,
            "words_per_section": self.words_per_section,
            "tone": self.tone,
            "include_edge_decorations": self.include_edge_decorations,
            "watermark_type": self.watermark_type,
            "watermark_text": self.watermark_text,
            "watermark_image_path": self.watermark_image_path,
            "watermark_opacity": self.watermark_opacity,
            "redaction_enabled": self.redaction_enabled,
            "redaction_rules": [
                {
                    "pattern": rule.pattern,
                    "replacement": rule.replacement,
                    "rule_type": rule.rule_type
                }
                for rule in self.redaction_rules
            ],
            "pii_types_to_redact": self.pii_types_to_redact,
            "color_scheme": self.color_scheme,
            "logo_path": self.logo_path,
            "output_format": self.output_format,
            "import_file_path": self.import_file_path,
            "user_id": self.user_id
        }