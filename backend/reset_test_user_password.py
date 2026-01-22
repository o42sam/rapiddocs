"""
Reset test user password to 'testuser' in MongoDB.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

async def reset_password():
    """Reset test user password."""
    # Connect to MongoDB
    mongodb_url = os.environ.get('MONGODB_URL')
    db_name = os.environ.get('MONGODB_DB_NAME', 'docgen')

    print(f"Connecting to MongoDB...")
    client = AsyncIOMotorClient(
        mongodb_url,
        server_api=ServerApi('1'),
        serverSelectionTimeoutMS=30000
    )

    db = client[db_name]

    # Find test user
    user = await db.users.find_one({'email': 'test@rapiddocs.io'})

    if user:
        print(f"✅ Found user: {user.get('email')}")

        # Generate new bcrypt hash for 'testuser'
        password = 'testuser'
        salt = bcrypt.gensalt()
        new_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        print(f"Generating new password hash...")
        print(f"  New hash starts with: {new_hash[:30]}...")

        # Update both password fields for compatibility
        result = await db.users.update_one(
            {'email': 'test@rapiddocs.io'},
            {
                '$set': {
                    'hashed_password': new_hash,
                    'password': new_hash,  # For backward compatibility
                    'password_hash': new_hash  # For new system
                }
            }
        )

        if result.modified_count > 0:
            print(f"✅ Password updated successfully!")

            # Verify it worked
            print(f"\nVerifying new password...")
            updated_user = await db.users.find_one({'email': 'test@rapiddocs.io'})
            stored_hash = updated_user.get('hashed_password', '')

            is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            print(f"  Password 'testuser' now valid: {'✅ YES' if is_valid else '❌ NO'}")
        else:
            print(f"❌ Failed to update password")
    else:
        print(f"❌ User test@rapiddocs.io not found")

        # Create the user if not exists
        print("\nWould you like to create the test user? (uncomment code below)")
        # Uncomment to create user:
        # password = 'testuser'
        # salt = bcrypt.gensalt()
        # password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        #
        # new_user = {
        #     'email': 'test@rapiddocs.io',
        #     'username': 'testuser',
        #     'name': 'Test User',
        #     'hashed_password': password_hash,
        #     'password': password_hash,
        #     'password_hash': password_hash,
        #     'is_active': True,
        #     'is_verified': True,
        #     'credits': 100,
        #     'subscription_tier': 'free'
        # }
        #
        # result = await db.users.insert_one(new_user)
        # print(f"✅ Created test user with ID: {result.inserted_id}")

    client.close()

if __name__ == "__main__":
    asyncio.run(reset_password())