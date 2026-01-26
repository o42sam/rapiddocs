"""Admin authentication and management routes."""

from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.auth import (
    AdminLogin,
    AdminRegister,
    AdminResponse,
    Token,
    ReferralKeyCreate,
    ReferralKeyResponse,
    DashboardStats
)
from app.services.auth_service import AuthService
from app.middleware.auth import security, get_current_admin, require_superuser


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/login", response_model=Token)
async def login(request: Request, credentials: AdminLogin):
    """Admin login endpoint."""
    auth_service: AuthService = request.app.state.auth_service

    admin = await auth_service.authenticate_admin(credentials.username, credentials.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Create tokens
    token_data = {
        "username": admin.username,
        "admin_id": str(admin.id),
        "permissions": admin.permissions
    }
    access_token = auth_service.create_access_token(token_data)
    refresh_token = auth_service.create_refresh_token(token_data)

    # Log session
    await request.app.state.db.admin_sessions.insert_one({
        "admin_id": str(admin.id),
        "username": admin.username,
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent", ""),
        "login_time": datetime.utcnow(),
        "last_activity": datetime.utcnow(),
        "is_active": True
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/register", response_model=AdminResponse)
async def register(request: Request, registration: AdminRegister):
    """Register a new admin with referral key."""
    auth_service: AuthService = request.app.state.auth_service

    admin = await auth_service.create_admin(
        username=registration.username,
        email=registration.email,
        password=registration.password,
        full_name=registration.full_name,
        referral_key=registration.referral_key
    )

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid referral key, expired key, or username/email already exists"
        )

    return AdminResponse(
        id=str(admin.id),
        username=admin.username,
        email=admin.email,
        full_name=admin.full_name,
        is_active=admin.is_active,
        is_superuser=admin.is_superuser,
        created_at=admin.created_at,
        last_login=admin.last_login,
        permissions=admin.permissions
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh access token using refresh token."""
    auth_service: AuthService = request.app.state.auth_service

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required"
        )

    token_data = auth_service.decode_token(credentials.credentials, token_type="refresh")
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Create new tokens
    new_token_data = {
        "username": token_data["username"],
        "admin_id": token_data["admin_id"],
        "permissions": token_data["permissions"]
    }
    access_token = auth_service.create_access_token(new_token_data)
    refresh_token = auth_service.create_refresh_token(new_token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current admin information."""
    auth_service: AuthService = request.app.state.auth_service

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    token_data = auth_service.decode_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    admin = await auth_service.get_admin_by_username(token_data["username"])
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )

    return AdminResponse(
        id=str(admin.id),
        username=admin.username,
        email=admin.email,
        full_name=admin.full_name,
        is_active=admin.is_active,
        is_superuser=admin.is_superuser,
        created_at=admin.created_at,
        last_login=admin.last_login,
        permissions=admin.permissions
    )


@router.post("/referral-key", response_model=ReferralKeyResponse)
async def create_referral_key(
    request: Request,
    key_data: ReferralKeyCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new referral key (any admin can create)."""
    auth_service: AuthService = request.app.state.auth_service

    token_data = auth_service.decode_token(credentials.credentials)
    admin = await auth_service.get_admin_by_username(token_data["username"])

    key = await auth_service.create_referral_key(
        created_by=admin.username,
        max_uses=key_data.max_uses,
        expires_in_days=key_data.expires_in_days,
        notes=key_data.notes
    )

    return ReferralKeyResponse(
        key=key.key,
        created_by=key.created_by,
        created_at=key.created_at,
        is_active=key.is_active,
        max_uses=key.max_uses,
        current_uses=key.current_uses,
        expires_at=key.expires_at,
        notes=key.notes
    )


@router.get("/referral-keys", response_model=List[ReferralKeyResponse])
async def get_referral_keys(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all referral keys created by the current admin."""
    auth_service: AuthService = request.app.state.auth_service

    token_data = auth_service.decode_token(credentials.credentials)
    admin = await auth_service.get_admin_by_username(token_data["username"])

    # Superusers can see all keys, others only their own
    created_by = None if admin.is_superuser else admin.username
    keys = await auth_service.get_active_referral_keys(created_by)

    return [
        ReferralKeyResponse(
            key=key.key,
            created_by=key.created_by,
            created_at=key.created_at,
            is_active=key.is_active,
            max_uses=key.max_uses,
            current_uses=key.current_uses,
            expires_at=key.expires_at,
            notes=key.notes
        )
        for key in keys
    ]


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get dashboard statistics (admin only)."""
    auth_service: AuthService = request.app.state.auth_service
    db = request.app.state.db

    # Verify admin
    token_data = auth_service.decode_token(credentials.credentials)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Calculate date ranges
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=now.weekday())
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Get statistics
    total_users = await db.users.count_documents({})
    total_admins = await db.admins.count_documents({})
    active_admins = await db.admins.count_documents({"is_active": True})

    # Active users (based on sessions)
    daily_active = await db.admin_sessions.count_documents({
        "last_activity": {"$gte": today_start}
    })
    weekly_active = await db.admin_sessions.count_documents({
        "last_activity": {"$gte": week_start}
    })
    monthly_active = await db.admin_sessions.count_documents({
        "last_activity": {"$gte": month_start}
    })

    # Document generation stats (from generation_jobs collection if exists)
    total_docs = await db.generation_jobs.count_documents({}) if "generation_jobs" in await db.list_collection_names() else 0
    docs_today = await db.generation_jobs.count_documents({
        "created_at": {"$gte": today_start}
    }) if "generation_jobs" in await db.list_collection_names() else 0
    docs_week = await db.generation_jobs.count_documents({
        "created_at": {"$gte": week_start}
    }) if "generation_jobs" in await db.list_collection_names() else 0
    docs_month = await db.generation_jobs.count_documents({
        "created_at": {"$gte": month_start}
    }) if "generation_jobs" in await db.list_collection_names() else 0

    # Calculate uptime (from app start time)
    uptime = datetime.utcnow() - request.app.state.start_time
    uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m"

    return DashboardStats(
        total_users=total_users,
        daily_active_users=daily_active,
        weekly_active_users=weekly_active,
        monthly_active_users=monthly_active,
        total_documents_generated=total_docs,
        documents_today=docs_today,
        documents_this_week=docs_week,
        documents_this_month=docs_month,
        total_admins=total_admins,
        active_admins=active_admins,
        server_uptime=uptime_str,
        last_deployment=request.app.state.start_time
    )


@router.delete("/referral-key/{key}")
async def delete_referral_key(
    request: Request,
    key: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete a referral key."""
    auth_service: AuthService = request.app.state.auth_service
    db = request.app.state.db

    # Verify admin
    token_data = auth_service.decode_token(credentials.credentials)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    admin = await auth_service.get_admin_by_username(token_data["username"])
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # Find the referral key
    ref_key = await db.referral_keys.find_one({"key": key})
    if not ref_key:
        raise HTTPException(status_code=404, detail="Referral key not found")

    # Check permissions: only the creator or a superuser can delete
    if ref_key["created_by"] != admin.username and not admin.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own referral keys"
        )

    # Delete the key
    result = await db.referral_keys.delete_one({"key": key})
    if result.deleted_count == 0:
        raise HTTPException(status_code=500, detail="Failed to delete referral key")

    return {"message": "Referral key deleted successfully"}


@router.post("/logout")
async def logout(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout current admin."""
    auth_service: AuthService = request.app.state.auth_service
    db = request.app.state.db

    token_data = auth_service.decode_token(credentials.credentials)
    if token_data:
        # Mark session as logged out
        await db.admin_sessions.update_one(
            {
                "admin_id": token_data["admin_id"],
                "is_active": True
            },
            {
                "$set": {
                    "logout_time": datetime.utcnow(),
                    "is_active": False
                }
            }
        )

    return {"message": "Logged out successfully"}