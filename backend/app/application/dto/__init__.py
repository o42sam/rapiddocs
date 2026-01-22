"""
Application DTOs (Data Transfer Objects).
Used for communication between layers.
"""

from .invoice_request import InvoiceRequest
from .infographic_request import InfographicRequest
from .formal_request import FormalRequest
from .generation_response import GenerationResponse, JobResponse

__all__ = [
    "InvoiceRequest",
    "InfographicRequest",
    "FormalRequest",
    "GenerationResponse",
    "JobResponse"
]