#!/usr/bin/env python3
"""
Detailed MongoDB Atlas connection diagnostic
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

async def detailed_test():
    mongodb_url = os.getenv('MONGODB_URL')
    db_name = os.getenv('MONGODB_DB_NAME')

    print("=" * 60)
    print("MongoDB Atlas Connection Diagnostic")
    print("=" * 60)
    print(f"Database name: {db_name}")
    print(f"Connection URL: {mongodb_url[:50]}...")
    print()

    try:
        print("[1/4] Creating MongoDB client...")
        client = AsyncIOMotorClient(
            mongodb_url,
            serverSelectionTimeoutMS=10000  # 10 second timeout
        )
        print("✓ Client created")

        print("\n[2/4] Testing connection with ping...")
        result = await client.admin.command('ping')
        print(f"✓ Ping successful: {result}")

        print("\n[3/4] Accessing database...")
        db = client[db_name]
        print(f"✓ Database accessed: {db_name}")

        print("\n[4/4] Listing collections...")
        collections = await db.list_collection_names()
        print(f"✓ Collections: {collections if collections else '(empty - new database)'}")

        client.close()

        print("\n" + "=" * 60)
        print("✅ SUCCESS! MongoDB Atlas connection working!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ CONNECTION FAILED")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

        if "timeout" in str(e).lower():
            print("\n💡 Diagnosis: Connection timeout")
            print("Possible causes:")
            print("  1. IP address not whitelisted in MongoDB Atlas")
            print(f"     Your IP: 102.88.55.248")
            print("  2. Firewall blocking outbound connection")
            print("  3. Cluster is paused or doesn't exist")
        elif "dns" in str(e).lower() or "getaddrinfo" in str(e).lower():
            print("\n💡 Diagnosis: DNS resolution failure")
            print("Possible causes:")
            print("  1. Cluster hostname is incorrect")
            print("  2. Cluster has been deleted")
            print("  3. DNS server issues")
        elif "auth" in str(e).lower():
            print("\n💡 Diagnosis: Authentication failure")
            print("Possible causes:")
            print("  1. Incorrect username or password")
            print("  2. User doesn't have proper permissions")

        print("\n" + "=" * 60)
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(detailed_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
