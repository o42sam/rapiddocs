"""Schemas module for API request/response validation."""

from .auth import (
    AdminLogin,
    AdminRegister,
    Token,
    TokenData,
    AdminResponse,
    ReferralKeyCreate,
    ReferralKeyResponse,
    DashboardStats
)

__all__ = [
    "AdminLogin",
    "AdminRegister",
    "Token",
    "TokenData",
    "AdminResponse",
    "ReferralKeyCreate",
    "ReferralKeyResponse",
    "DashboardStats"
]