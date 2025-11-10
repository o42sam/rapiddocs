"""
Activate all user accounts in the database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

async def activate_all_users():
    """Activate all user accounts"""
    mongodb_url = os.getenv("MONGODB_URL")
    client = AsyncIOMotorClient(mongodb_url)
    db = client.get_database("docgen")

    print("=" * 60)
    print("Activating All User Accounts")
    print("=" * 60)

    # Update all users to be active and verified
    result = await db.users.update_many(
        {},  # Update all users
        {
            "$set": {
                "is_active": True,
                "is_verified": True,
                "updated_at": datetime.utcnow()
            }
        }
    )

    print(f"\n✅ Updated {result.matched_count} user accounts")
    print(f"✅ Modified {result.modified_count} user accounts")

    # Show all users
    users = db.users.find({})
    print("\n" + "=" * 60)
    print("Current Users:")
    print("=" * 60)

    count = 0
    async for user in users:
        count += 1
        print(f"\n{count}. {user['email']}")
        print(f"   ID: {user['_id']}")
        print(f"   Active: {user.get('is_active', False)}")
        print(f"   Verified: {user.get('is_verified', False)}")
        print(f"   Credits: {user.get('credits', 0)}")

    print("\n" + "=" * 60)
    print(f"Total users: {count}")
    print("=" * 60)

    client.close()

if __name__ == "__main__":
    asyncio.run(activate_all_users())
