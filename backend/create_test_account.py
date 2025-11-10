"""
Create a test account with infinite credits
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test account credentials
TEST_EMAIL = "test@rapiddocs.io"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "TestPass123!"
INFINITE_CREDITS = 999999999  # Effectively infinite

async def create_test_account():
    """Create a test account with infinite credits"""

    # Connect to MongoDB
    mongodb_url = os.getenv("MONGODB_URL")
    client = AsyncIOMotorClient(mongodb_url)
    db = client.get_database("docgen")

    print("=" * 60)
    print("Creating Test Account with Infinite Credits")
    print("=" * 60)

    # Check if account already exists
    existing_user = await db.users.find_one({"email": TEST_EMAIL})

    if existing_user:
        # Update existing account with infinite credits
        await db.users.update_one(
            {"email": TEST_EMAIL},
            {
                "$set": {
                    "credits": INFINITE_CREDITS,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        print(f"\n✅ Updated existing account: {TEST_EMAIL}")
        print(f"✅ Credits set to: {INFINITE_CREDITS:,}")
    else:
        # Create new account
        hashed_password = pwd_context.hash(TEST_PASSWORD)

        test_user = {
            "email": TEST_EMAIL,
            "username": TEST_USERNAME,
            "hashed_password": hashed_password,
            "full_name": "Test User",
            "credits": INFINITE_CREDITS,
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = await db.users.insert_one(test_user)
        print(f"\n✅ Created new account: {TEST_EMAIL}")
        print(f"✅ User ID: {result.inserted_id}")
        print(f"✅ Credits: {INFINITE_CREDITS:,}")

    print("\n" + "=" * 60)
    print("Test Account Credentials:")
    print("=" * 60)
    print(f"Email:    {TEST_EMAIL}")
    print(f"Password: {TEST_PASSWORD}")
    print(f"Credits:  {INFINITE_CREDITS:,} (Infinite)")
    print("=" * 60)
    print("\nDocument Generation Costs:")
    print("  • Formal Document:     34 credits")
    print("  • Infographic:         52 credits")
    print(f"\nDocuments you can generate: {INFINITE_CREDITS // 52:,}+")
    print("=" * 60)

    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(create_test_account())
