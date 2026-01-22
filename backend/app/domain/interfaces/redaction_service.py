"""
Redaction Service Interface.
Defines the contract for text redaction operations.
"""

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
        """
        Redact text matching regex patterns.

        Args:
            text: Input text to redact
            patterns: List of regex patterns
            replacement: Replacement string

        Returns:
            Redacted text
        """
        pass

    @abstractmethod
    def redact_pii(
        self,
        text: str,
        pii_types: List[str]
    ) -> str:
        """
        Redact personally identifiable information.

        Args:
            text: Input text to redact
            pii_types: List of PII types to redact (e.g., ['email', 'phone', 'ssn'])

        Returns:
            Text with PII redacted
        """
        pass

    @abstractmethod
    def redact_custom(
        self,
        text: str,
        redaction_rules: List[Dict[str, Any]]
    ) -> str:
        """
        Apply custom redaction rules.

        Args:
            text: Input text to redact
            redaction_rules: List of custom redaction rules

        Returns:
            Redacted text
        """
        pass

    @property
    @abstractmethod
    def supported_pii_types(self) -> List[str]:
        """Return list of supported PII types for redaction."""
        pass