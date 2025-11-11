"""
Check generation jobs in database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

async def check_jobs():
    """Check recent generation jobs"""
    mongodb_url = os.getenv("MONGODB_URL")
    client = AsyncIOMotorClient(mongodb_url)
    db = client.get_database("docgen")

    print("=" * 60)
    print("Recent Generation Jobs")
    print("=" * 60)

    # Get last 10 jobs
    jobs = db.generation_jobs.find().sort("created_at", -1).limit(10)

    count = 0
    async for job in jobs:
        count += 1
        print(f"\n{count}. Job ID: {job['_id']}")
        print(f"   Document ID: {job.get('document_id')}")
        print(f"   Status: {job.get('status')}")
        print(f"   Progress: {job.get('progress')}%")
        print(f"   Current Step: {job.get('current_step')}")
        print(f"   Created: {job.get('created_at', 'N/A')}")
        if job.get('error_message'):
            print(f"   Error: {job.get('error_message')}")

    if count == 0:
        print("\nNo jobs found in database!")

    print("\n" + "=" * 60)
    print(f"Total recent jobs: {count}")
    print("=" * 60)

    # Check documents too
    print("\nRecent Documents:")
    print("=" * 60)

    docs = db.documents.find().sort("created_at", -1).limit(5)
    doc_count = 0
    async for doc in docs:
        doc_count += 1
        print(f"\n{doc_count}. Doc ID: {doc['_id']}")
        print(f"   Title: {doc.get('title')}")
        print(f"   Status: {doc.get('status')}")
        print(f"   User ID: {doc.get('user_id')}")
        print(f"   Created: {doc.get('created_at', 'N/A')}")

    print("\n" + "=" * 60)

    client.close()

if __name__ == "__main__":
    asyncio.run(check_jobs())
