#!/usr/bin/env python3
"""
Test document generation with MongoDB Atlas
"""
import requests
import json
import time
import os

API_BASE_URL = "http://localhost:8000/api/v1"

def test_document_generation():
    print("=" * 60)
    print("Testing Document Generation with MongoDB Atlas")
    print("=" * 60)
    print()

    # Prepare test data
    description = "Create a test whitepaper about AI-powered document generation systems and their impact on business efficiency."
    length = 1000  # 1000 words for a quick test
    document_type = "formal"
    use_watermark = False  # No watermark for simple test

    statistics = []
    design_spec = {
        "background_color": "#FFFFFF",
        "foreground_color_1": "#2563EB",
        "foreground_color_2": "#06B6D4"
    }

    # Prepare form data
    data = {
        "description": description,
        "length": length,
        "document_type": document_type,
        "use_watermark": str(use_watermark).lower(),
        "statistics": json.dumps(statistics),
        "design_spec": json.dumps(design_spec)
    }

    print("[1/4] Sending document generation request...")
    print(f"  Description: {description[:50]}...")
    print(f"  Length: {length} words")
    print(f"  Type: {document_type}")
    print()

    try:
        response = requests.post(
            f"{API_BASE_URL}/generate/document",
            data=data,
            timeout=30
        )

        if response.status_code != 200:
            print(f"✗ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

        result = response.json()
        job_id = result.get("job_id")
        print(f"✓ Document generation started")
        print(f"  Job ID: {job_id}")
        print()

        # Poll for completion
        print("[2/4] Polling for completion...")
        max_wait = 300  # 5 minutes max
        start_time = time.time()
        last_progress = -1

        while time.time() - start_time < max_wait:
            status_response = requests.get(
                f"{API_BASE_URL}/generate/status/{job_id}",
                timeout=10
            )

            if status_response.status_code != 200:
                print(f"✗ Status check failed: {status_response.status_code}")
                return False

            status = status_response.json()
            current_status = status.get("status")
            progress = status.get("progress", 0)
            current_step = status.get("current_step", "")

            if progress != last_progress:
                print(f"  Progress: {progress}% - {current_step}")
                last_progress = progress

            if current_status == "completed":
                print(f"✓ Document generation completed!")
                print()
                break
            elif current_status == "failed":
                error = status.get("error_message", "Unknown error")
                print(f"✗ Document generation failed: {error}")
                return False

            time.sleep(2)  # Poll every 2 seconds
        else:
            print(f"✗ Timeout waiting for completion")
            return False

        # Download document
        print("[3/4] Downloading generated PDF...")
        download_response = requests.get(
            f"{API_BASE_URL}/generate/download/{job_id}",
            timeout=10
        )

        if download_response.status_code != 200:
            print(f"✗ Download failed: {download_response.status_code}")
            return False

        # Save to test file
        test_pdf_path = "/tmp/test_generated_document.pdf"
        with open(test_pdf_path, 'wb') as f:
            f.write(download_response.content)

        file_size = len(download_response.content)
        print(f"✓ PDF downloaded successfully")
        print(f"  Size: {file_size:,} bytes")
        print(f"  Saved to: {test_pdf_path}")
        print()

        # Verify MongoDB storage
        print("[4/4] Verifying MongoDB Atlas storage...")
        import asyncio
        from motor.motor_asyncio import AsyncIOMotorClient
        from dotenv import load_dotenv

        load_dotenv()

        async def check_db():
            mongodb_url = os.getenv('MONGODB_URL')
            db_name = os.getenv('MONGODB_DB_NAME')

            client = AsyncIOMotorClient(mongodb_url)
            db = client[db_name]

            doc_count = await db.documents.count_documents({})
            job_count = await db.generation_jobs.count_documents({})

            print(f"✓ Documents in MongoDB Atlas: {doc_count}")
            print(f"✓ Jobs in MongoDB Atlas: {job_count}")

            if doc_count > 0:
                latest_doc = await db.documents.find_one(
                    {},
                    sort=[('created_at', -1)]
                )
                print(f"\nLatest Document:")
                print(f"  ID: {latest_doc['_id']}")
                print(f"  Title: {latest_doc.get('title', 'N/A')}")
                print(f"  Status: {latest_doc.get('status', 'N/A')}")

            client.close()
            return doc_count > 0

        success = asyncio.run(check_db())
        print()

        if success:
            print("=" * 60)
            print("✅ SUCCESS! Complete workflow verified!")
            print("=" * 60)
            print("\nWorkflow Summary:")
            print("  ✓ API request successful")
            print("  ✓ Background job processing")
            print("  ✓ PDF generation complete")
            print("  ✓ PDF download working")
            print("  ✓ Data stored in MongoDB Atlas")
            return True
        else:
            print("✗ Document not found in MongoDB Atlas")
            return False

    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_document_generation()
    sys.exit(0 if success else 1)
