#!/usr/bin/env python3
"""Script to create a test user in the docgen_prod database with infinite credits."""

import asyncio
import motor.motor_asyncio
from datetime import datetime
import hashlib

# MongoDB connection string (production)
MONGODB_URL = "mongodb+srv://samscarfaceegbo:G7a1n14G7@cluster1.vehwbxh.mongodb.net/?appName=Cluster1"
MONGODB_DB_NAME = "docgen_prod"

async def create_test_user():
    """Create a test user with infinite credits."""
    try:
        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
        db = client[MONGODB_DB_NAME]

        print(f"Connected to MongoDB database: {MONGODB_DB_NAME}")

        # Check if test user already exists
        existing_user = await db.users.find_one({"email": "test@rapiddocs.io"})

        if existing_user:
            print(f"Test user already exists with ID: {existing_user['_id']}")
            # Update existing user with infinite credits
            result = await db.users.update_one(
                {"email": "test@rapiddocs.io"},
                {
                    "$set": {
                        "credits": 999999,  # Infinite credits (large number)
                        "subscription_tier": "premium",
                        "is_test_user": True,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            if result.modified_count > 0:
                print("✅ Updated existing test user with infinite credits!")
        else:
            # Create new test user
            # Simple password hash for testing (in production, use bcrypt)
            password_hash = hashlib.sha256("testuser".encode()).hexdigest()

            user_data = {
                "email": "test@rapiddocs.io",
                "username": "testuser",
                "password": password_hash,  # Simple hash for testing
                "full_name": "Test User",
                "credits": 999999,  # Infinite credits (large number)
                "subscription_tier": "premium",
                "is_test_user": True,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": None,
                "documents_generated": 0,
                "preferences": {
                    "default_format": "pdf",
                    "enable_watermark": False,
                    "email_notifications": True
                }
            }

            result = await db.users.insert_one(user_data)
            print(f"✅ Created new test user with ID: {result.inserted_id}")

        # Also ensure credits collection has an entry
        credits_entry = await db.credits.find_one({"user_email": "test@rapiddocs.io"})

        if not credits_entry:
            await db.credits.insert_one({
                "user_email": "test@rapiddocs.io",
                "total_credits": 999999,
                "used_credits": 0,
                "remaining_credits": 999999,
                "credit_history": [
                    {
                        "action": "initial_grant",
                        "amount": 999999,
                        "timestamp": datetime.utcnow(),
                        "description": "Test user infinite credits"
                    }
                ],
                "last_updated": datetime.utcnow()
            })
            print("✅ Created credits entry for test user")
        else:
            # Update existing credits
            await db.credits.update_one(
                {"user_email": "test@rapiddocs.io"},
                {
                    "$set": {
                        "total_credits": 999999,
                        "remaining_credits": 999999,
                        "last_updated": datetime.utcnow()
                    }
                }
            )
            print("✅ Updated credits for test user")

        print("\n" + "="*60)
        print("TEST USER CREDENTIALS")
        print("="*60)
        print("Email: test@rapiddocs.io")
        print("Password: testuser")
        print("Credits: 999,999 (effectively infinite)")
        print("Access: All document types (invoice, infographic, formal)")
        print("="*60)
        print("\nTest user is ready for testing all document generation workflows!")

        client.close()
        return True

    except Exception as e:
        print(f"Error creating test user: {e}")
        return False

async def verify_user_auth():
    """Verify that the user can be authenticated."""
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
        db = client[MONGODB_DB_NAME]

        # Check if user exists
        user = await db.users.find_one({"email": "test@rapiddocs.io"})
        if user:
            print("\n✅ User verification:")
            print(f"   - Email: {user['email']}")
            print(f"   - Credits: {user.get('credits', 0):,}")
            print(f"   - Status: Active" if user.get('is_active', True) else "   - Status: Inactive")
            print(f"   - Test User: Yes" if user.get('is_test_user', False) else "   - Test User: No")
        else:
            print("\n❌ User not found in database")

        client.close()

    except Exception as e:
        print(f"Error verifying user: {e}")

if __name__ == "__main__":
    asyncio.run(create_test_user())
    asyncio.run(verify_user_auth())