"""Authentication service for admin users."""

import secrets
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.admin import AdminUser, ReferralKey
from app.config import settings


class AuthService:
    """Service for handling authentication operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = settings.JWT_SECRET_KEY
        self.REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY
        self.ALGORITHM = settings.JWT_ALGORITHM
        self.ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.REFRESH_SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str, token_type: str = "access") -> Optional[dict]:
        """Decode and validate a JWT token."""
        try:
            secret = self.SECRET_KEY if token_type == "access" else self.REFRESH_SECRET_KEY
            payload = jwt.decode(token, secret, algorithms=[self.ALGORITHM])
            if payload.get("type") != token_type:
                return None
            return payload
        except JWTError:
            return None

    async def authenticate_admin(self, username: str, password: str) -> Optional[AdminUser]:
        """Authenticate an admin user."""
        admin = await self.db.admins.find_one({"username": username})
        if not admin:
            return None
        if not self.verify_password(password, admin["hashed_password"]):
            return None

        # Update last login
        await self.db.admins.update_one(
            {"_id": admin["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        return AdminUser(**admin)

    async def create_admin(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str,
        referral_key: str,
        is_superuser: bool = False
    ) -> Optional[AdminUser]:
        """Create a new admin user with referral key validation."""
        # Check if referral key is valid
        ref_key = await self.db.referral_keys.find_one({
            "key": referral_key,
            "is_active": True
        })

        if not ref_key:
            return None

        # Check if key has expired
        if ref_key.get("expires_at") and ref_key["expires_at"] < datetime.utcnow():
            return None

        # Check if key has reached max uses
        if ref_key["current_uses"] >= ref_key["max_uses"]:
            return None

        # Check if username or email already exists
        existing = await self.db.admins.find_one({
            "$or": [
                {"username": username},
                {"email": email}
            ]
        })
        if existing:
            return None

        # Create admin user
        admin = AdminUser(
            username=username,
            email=email,
            hashed_password=self.get_password_hash(password),
            full_name=full_name,
            is_superuser=is_superuser,
            created_by_referral=referral_key,
            permissions=["docs:read", "health:read"] if not is_superuser else ["*"]
        )

        result = await self.db.admins.insert_one(admin.dict(by_alias=True))
        admin.id = result.inserted_id

        # Update referral key usage
        await self.db.referral_keys.update_one(
            {"_id": ref_key["_id"]},
            {
                "$set": {
                    "used_at": datetime.utcnow(),
                    "used_by": username
                },
                "$inc": {"current_uses": 1}
            }
        )

        # Deactivate key if it reached max uses
        if ref_key["current_uses"] + 1 >= ref_key["max_uses"]:
            await self.db.referral_keys.update_one(
                {"_id": ref_key["_id"]},
                {"$set": {"is_active": False}}
            )

        return admin

    async def get_admin_by_username(self, username: str) -> Optional[AdminUser]:
        """Get admin user by username."""
        admin = await self.db.admins.find_one({"username": username})
        if admin:
            return AdminUser(**admin)
        return None

    async def create_referral_key(
        self,
        created_by: str,
        max_uses: int = 1,
        expires_in_days: Optional[int] = None,
        notes: Optional[str] = None
    ) -> ReferralKey:
        """Create a new referral key."""
        key = ReferralKey(
            key=secrets.token_urlsafe(32),
            created_by=created_by,
            max_uses=max_uses,
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days) if expires_in_days else None,
            notes=notes
        )

        result = await self.db.referral_keys.insert_one(key.dict(by_alias=True))
        key.id = result.inserted_id

        return key

    async def get_active_referral_keys(self, created_by: Optional[str] = None):
        """Get all active referral keys."""
        query = {"is_active": True}
        if created_by:
            query["created_by"] = created_by

        cursor = self.db.referral_keys.find(query)
        keys = []
        async for key in cursor:
            keys.append(ReferralKey(**key))
        return keys

    async def create_initial_superuser(self) -> Optional[tuple]:
        """Create the initial superuser with a referral key."""
        # Check if any admin exists
        admin_count = await self.db.admins.count_documents({})
        if admin_count > 0:
            return None

        # Create initial referral key
        initial_key = secrets.token_urlsafe(32)
        ref_key = ReferralKey(
            key=initial_key,
            created_by="system",
            max_uses=1,
            notes="Initial superuser registration key"
        )
        await self.db.referral_keys.insert_one(ref_key.dict(by_alias=True))

        return ("system", initial_key)