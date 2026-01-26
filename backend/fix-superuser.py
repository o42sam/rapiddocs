#!/usr/bin/env python3
"""Script to update an existing admin to superuser status."""

import asyncio
import motor.motor_asyncio
from datetime import datetime
import sys

# MongoDB connection string (same as in .env.production)
MONGODB_URL = "mongodb+srv://rapiddocs:rapidpass@cluster0.ctxlu.mongodb.net/?retryWrites=true&w=majority"
MONGODB_DB_NAME = "docgen_prod"

async def update_admin_to_superuser(username: str):
    """Update an admin user to superuser status."""
    try:
        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
        db = client[MONGODB_DB_NAME]

        print(f"Connected to MongoDB database: {MONGODB_DB_NAME}")

        # Find the admin by username
        admin = await db.admins.find_one({"username": username})

        if not admin:
            print(f"Error: Admin with username '{username}' not found!")
            return False

        # Check if already superuser
        if admin.get("is_superuser"):
            print(f"Admin '{username}' is already a superuser!")
            return True

        # Update to superuser
        result = await db.admins.update_one(
            {"username": username},
            {
                "$set": {
                    "is_superuser": True,
                    "permissions": ["*"],
                    "updated_at": datetime.utcnow()
                }
            }
        )

        if result.modified_count > 0:
            print(f"✅ Successfully updated '{username}' to superuser status!")
            print(f"   - is_superuser: True")
            print(f"   - permissions: ['*'] (all permissions)")
            return True
        else:
            print(f"Error: Failed to update admin '{username}'")
            return False

    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False
    finally:
        client.close()

async def list_all_admins():
    """List all admin users in the database."""
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
        db = client[MONGODB_DB_NAME]

        print("\nCurrent admin users:")
        print("-" * 50)

        cursor = db.admins.find({})
        count = 0
        async for admin in cursor:
            count += 1
            superuser_status = "✓ SUPERUSER" if admin.get("is_superuser") else "regular"
            print(f"  {count}. {admin['username']} ({admin['email']}) - {superuser_status}")

        if count == 0:
            print("  No admin users found in database.")

        print("-" * 50)
        return count > 0

    except Exception as e:
        print(f"Error listing admins: {e}")
        return False
    finally:
        client.close()

async def main():
    """Main function."""
    print("=" * 60)
    print("RapidDocs - Update Admin to Superuser")
    print("=" * 60)

    # List current admins
    has_admins = await list_all_admins()

    if not has_admins:
        print("\nNo admin users found. Please register an admin first.")
        return

    # Get username from command line or prompt
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("\nEnter the username to make superuser: ").strip()

    if not username:
        print("Error: Username cannot be empty!")
        return

    # Update the admin
    print(f"\nUpdating '{username}' to superuser...")
    success = await update_admin_to_superuser(username)

    if success:
        print("\n✅ Update complete! The admin can now:")
        print("   - Create referral keys")
        print("   - Access all admin features")
        print("   - Manage other admins")
        print("\nPlease log out and log back in for changes to take effect.")
    else:
        print("\n❌ Update failed. Please check the username and try again.")

if __name__ == "__main__":
    asyncio.run(main())