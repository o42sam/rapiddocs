"""Authentication middleware for protecting routes."""

from typing import Optional
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import AuthService


security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """Middleware for authenticating admin requests."""

    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    async def __call__(self, request: Request, credentials: Optional[HTTPAuthorizationCredentials] = None):
        """Verify admin authentication."""
        # Check if request is from allowed frontend origin
        origin = request.headers.get("origin", "")
        referer = request.headers.get("referer", "")

        # List of allowed frontend origins that don't need admin auth
        allowed_origins = [
            "https://rapiddocs.web.app",
            "https://rapiddocs.firebaseapp.com",
            "https://rapiddocs.io",
            "https://www.rapiddocs.io",
            "http://localhost:5173",  # Development
            "http://localhost:5174"   # Development
        ]

        # If request is from allowed frontend, allow it
        for allowed in allowed_origins:
            if origin.startswith(allowed) or referer.startswith(allowed):
                return None  # Allow request without admin auth

        # Otherwise, require admin authentication
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Decode and validate token
        token_data = self.auth_service.decode_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get admin user
        admin = await self.auth_service.get_admin_by_username(token_data.get("username"))
        if not admin or not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin user not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Store admin in request state for use in routes
        request.state.admin = admin
        return admin


async def get_current_admin(request: Request) -> Optional[dict]:
    """Get current admin from request state."""
    return getattr(request.state, "admin", None)


async def require_superuser(request: Request):
    """Require that the current user is a superuser."""
    admin = await get_current_admin(request)
    if not admin or not admin.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required"
        )