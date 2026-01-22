"""
Domain exceptions.
Custom exceptions for domain-specific errors.
"""

from typing import Optional, Dict, Any


class DomainException(Exception):
    """Base class for domain exceptions."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationException(DomainException):
    """Exception raised for validation errors."""
    pass


class EntityNotFoundException(DomainException):
    """Exception raised when an entity is not found."""

    def __init__(self, entity_type: str, entity_id: str):
        super().__init__(
            f"{entity_type} with ID {entity_id} not found",
            {"entity_type": entity_type, "entity_id": entity_id}
        )


class InsufficientCreditsException(DomainException):
    """Exception raised when user has insufficient credits."""

    def __init__(self, required: int, available: int):
        super().__init__(
            f"Insufficient credits. Required: {required}, Available: {available}",
            {"required": required, "available": available}
        )


class GenerationException(DomainException):
    """Exception raised during document generation."""
    pass


class InvalidFormatException(DomainException):
    """Exception raised for invalid document format."""

    def __init__(self, format: str, supported_formats: list):
        super().__init__(
            f"Invalid format: {format}. Supported formats: {', '.join(supported_formats)}",
            {"format": format, "supported_formats": supported_formats}
        )


class FileProcessingException(DomainException):
    """Exception raised during file processing."""
    pass


class ExternalServiceException(DomainException):
    """Exception raised when external service fails."""

    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"External service '{service}' failed: {message}",
            {"service": service, **details} if details else {"service": service}
        )


class AuthenticationException(DomainException):
    """Exception raised for authentication failures."""
    pass


class AuthorizationException(DomainException):
    """Exception raised for authorization failures."""
    pass


class EntityExistsException(DomainException):
    """Exception raised when trying to create an entity that already exists."""

    def __init__(self, entity_type: str, identifier: str):
        super().__init__(
            f"{entity_type} with identifier {identifier} already exists",
            {"entity_type": entity_type, "identifier": identifier}
        )


class TokenException(DomainException):
    """Exception raised for token-related errors."""
    pass