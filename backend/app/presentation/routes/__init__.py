"""
Presentation Routes Module.
Contains API endpoint definitions.
"""

from . import infographic_routes
from . import generation_routes
from . import credits_routes

__all__ = [
    "infographic_routes",
    "generation_routes",
    "credits_routes"
]
