"""
Google OAuth2 service for authentication
"""
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config as StarletteConfig
from app.config import settings
from typing import Dict, Optional
import secrets

# Initialize OAuth
starlette_config = StarletteConfig(environ={
    "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
})

oauth = OAuth(starlette_config)

# Register Google OAuth
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


def generate_state_token() -> str:
    """
    Generate a secure random state token for CSRF protection

    Returns:
        str: Random state token
    """
    return secrets.token_urlsafe(32)


def get_google_auth_url(redirect_uri: str, state: str) -> str:
    """
    Generate Google OAuth authorization URL

    Args:
        redirect_uri: The callback URL
        state: CSRF protection token

    Returns:
        str: Authorization URL
    """
    authorization_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"state={state}&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    return authorization_url


async def exchange_code_for_token(code: str, redirect_uri: str) -> Optional[Dict]:
    """
    Exchange authorization code for access token

    Args:
        code: Authorization code from Google
        redirect_uri: The callback URL used in authorization

    Returns:
        Dict with token information or None on failure
    """
    try:
        import httpx

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            return response.json()

    except Exception as e:
        print(f"Error exchanging code for token: {e}")
        return None


async def get_google_user_info(access_token: str) -> Optional[Dict]:
    """
    Get user information from Google using access token

    Args:
        access_token: Google access token

    Returns:
        Dict with user information or None on failure
    """
    try:
        import httpx

        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(userinfo_url, headers=headers)
            response.raise_for_status()
            return response.json()

    except Exception as e:
        print(f"Error getting user info: {e}")
        return None


def generate_username_from_email(email: str, google_id: str) -> str:
    """
    Generate a unique username from email and Google ID

    Args:
        email: User's email address
        google_id: Google user ID

    Returns:
        str: Generated username
    """
    # Extract username part from email
    username_base = email.split('@')[0].lower()
    # Remove special characters
    username_base = ''.join(c for c in username_base if c.isalnum() or c in ['_', '-'])
    # Add first 8 chars of google_id for uniqueness
    username = f"{username_base}_{google_id[:8]}"
    return username
