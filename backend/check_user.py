"""
Check user information
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

async def check_user():
    """Check user with specific ID"""
    mongodb_url = os.getenv("MONGODB_URL")
    client = AsyncIOMotorClient(mongodb_url)
    db = client.get_database("docgen")

    # Check the user ID from the document
    user_id = "691241a258742827fa96ceda"
    
    print("=" * 60)
    print(f"Looking for user: {user_id}")
    print("=" * 60)
    
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            print(f"\n✅ Found user:")
            print(f"   ID: {user['_id']}")
            print(f"   Email: {user.get('email')}")
            print(f"   Username: {user.get('username')}")
            print(f"   Is Active: {user.get('is_active')}")
            print(f"   Is Verified: {user.get('is_verified')}")
            print(f"   Credits: {user.get('credits')}")
        else:
            print(f"\n❌ User not found with ID: {user_id}")
    except Exception as e:
        print(f"\n❌ Error looking up user: {str(e)}")

    # Also list ALL users
    print("\n" + "=" * 60)
    print("All users in database:")
    print("=" * 60)
    
    users = db.users.find()
    count = 0
    async for user in users:
        count += 1
        print(f"\n{count}. ID: {user['_id']}")
        print(f"   Email: {user.get('email')}")
        print(f"   Active: {user.get('is_active')}")
        print(f"   Credits: {user.get('credits')}")

    print(f"\nTotal users: {count}")
    print("=" * 60)

    client.close()

if __name__ == "__main__":
    asyncio.run(check_user())
