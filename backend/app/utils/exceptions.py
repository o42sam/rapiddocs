"""Custom exceptions for the document generation application"""


class DocumentGenerationError(Exception):
    """Base exception for document generation errors"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class TextGenerationError(DocumentGenerationError):
    """Raised when text generation fails"""
    pass


class ImageGenerationError(DocumentGenerationError):
    """Raised when image generation fails"""
    pass


class VisualizationError(DocumentGenerationError):
    """Raised when data visualization generation fails"""
    pass


class PDFGenerationError(DocumentGenerationError):
    """Raised when PDF assembly fails"""
    pass


class StorageError(DocumentGenerationError):
    """Raised when file storage operations fail"""
    pass


class ValidationError(DocumentGenerationError):
    """Raised when input validation fails"""
    pass
