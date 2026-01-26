#!/usr/bin/env python3
"""Script to create a test user for the frontend in the docgen_prod database."""

import asyncio
import motor.motor_asyncio
from datetime import datetime
from passlib.context import CryptContext
from bson import ObjectId

# MongoDB connection string (production)
MONGODB_URL = "mongodb+srv://samscarfaceegbo:G7a1n14G7@cluster1.vehwbxh.mongodb.net/?appName=Cluster1"
MONGODB_DB_NAME = "docgen_prod"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_frontend_test_user():
    """Create a test user that works with the frontend authentication."""
    try:
        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
        db = client[MONGODB_DB_NAME]

        print(f"Connected to MongoDB database: {MONGODB_DB_NAME}")

        # Check if test user already exists in users collection
        existing_user = await db.users.find_one({"email": "test@rapiddocs.io"})

        # Hash the password properly
        hashed_password = pwd_context.hash("testuser")

        if existing_user:
            print(f"Test user already exists with ID: {existing_user['_id']}")
            # Update existing user
            result = await db.users.update_one(
                {"email": "test@rapiddocs.io"},
                {
                    "$set": {
                        "password": hashed_password,  # Update password hash
                        "hashedPassword": hashed_password,  # Alternative field name
                        "credits": 999999,
                        "subscription_tier": "premium",
                        "is_test_user": True,
                        "is_active": True,
                        "emailVerified": True,
                        "updated_at": datetime.utcnow(),
                        "displayName": "Test User",
                        "fullName": "Test User",
                        "username": "testuser"
                    }
                }
            )
            if result.modified_count > 0:
                print("✅ Updated existing test user!")
        else:
            # Create new test user with proper structure
            user_data = {
                "_id": ObjectId(),
                "email": "test@rapiddocs.io",
                "username": "testuser",
                "password": hashed_password,  # Bcrypt hashed password
                "hashedPassword": hashed_password,  # Alternative field name
                "displayName": "Test User",
                "fullName": "Test User",
                "full_name": "Test User",
                "credits": 999999,
                "subscription_tier": "premium",
                "is_test_user": True,
                "is_active": True,
                "emailVerified": True,
                "created_at": datetime.utcnow(),
                "createdAt": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
                "last_login": None,
                "documents_generated": 0,
                "preferences": {
                    "default_format": "pdf",
                    "enable_watermark": False,
                    "email_notifications": True
                },
                "role": "user",
                "provider": "email"
            }

            result = await db.users.insert_one(user_data)
            print(f"✅ Created new test user with ID: {result.inserted_id}")

        # Ensure credits collection has proper entry
        credits_entry = await db.credits.find_one({"user_email": "test@rapiddocs.io"})

        if not credits_entry:
            await db.credits.insert_one({
                "_id": ObjectId(),
                "user_email": "test@rapiddocs.io",
                "user_id": str(existing_user['_id']) if existing_user else str(result.inserted_id),
                "total_credits": 999999,
                "used_credits": 0,
                "remaining_credits": 999999,
                "credit_history": [
                    {
                        "action": "initial_grant",
                        "amount": 999999,
                        "timestamp": datetime.utcnow(),
                        "description": "Test user infinite credits for testing"
                    }
                ],
                "last_updated": datetime.utcnow(),
                "created_at": datetime.utcnow()
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
                        "used_credits": 0,
                        "last_updated": datetime.utcnow()
                    }
                }
            )
            print("✅ Updated credits for test user")

        # Also ensure user sessions collection is ready
        await db.user_sessions.delete_many({"email": "test@rapiddocs.io"})
        print("✅ Cleared any old sessions for test user")

        print("\n" + "="*60)
        print("FRONTEND TEST USER CREDENTIALS")
        print("="*60)
        print("Email: test@rapiddocs.io")
        print("Password: testuser")
        print("Credits: 999,999 (effectively infinite)")
        print("Access Level: Premium (all document types)")
        print("Document Types: Invoice, Infographic, Formal")
        print("="*60)
        print("\nTest user is ready for frontend testing!")
        print("\nYou can now log in at https://rapiddocs.io with these credentials")

        client.close()
        return True

    except Exception as e:
        print(f"Error creating test user: {e}")
        import traceback
        traceback.print_exc()
        return False

async def verify_test_user():
    """Verify the test user setup."""
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
        db = client[MONGODB_DB_NAME]

        # Check user
        user = await db.users.find_one({"email": "test@rapiddocs.io"})
        if user:
            print("\n✅ User Verification:")
            print(f"   - ID: {user['_id']}")
            print(f"   - Email: {user['email']}")
            print(f"   - Username: {user.get('username', 'N/A')}")
            print(f"   - Credits: {user.get('credits', 0):,}")
            print(f"   - Active: {user.get('is_active', False)}")
            print(f"   - Email Verified: {user.get('emailVerified', False)}")
            print(f"   - Test User: {user.get('is_test_user', False)}")
            print(f"   - Has Password: {'Yes' if user.get('password') or user.get('hashedPassword') else 'No'}")
        else:
            print("\n❌ User not found")

        # Check credits
        credits = await db.credits.find_one({"user_email": "test@rapiddocs.io"})
        if credits:
            print("\n✅ Credits Verification:")
            print(f"   - Total Credits: {credits.get('total_credits', 0):,}")
            print(f"   - Used Credits: {credits.get('used_credits', 0):,}")
            print(f"   - Remaining: {credits.get('remaining_credits', 0):,}")
        else:
            print("\n❌ Credits entry not found")

        client.close()

    except Exception as e:
        print(f"Error verifying user: {e}")

if __name__ == "__main__":
    asyncio.run(create_frontend_test_user())
    asyncio.run(verify_test_user())