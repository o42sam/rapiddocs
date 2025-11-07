#!/usr/bin/env python3
"""
Test script for document type functionality

This script tests both formal and infographic document generation.
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000/api/v1"


def test_formal_document():
    """Test formal document generation"""
    print("\n" + "="*60)
    print("Testing FORMAL Document Generation")
    print("="*60)

    payload = {
        "description": "Create a comprehensive quarterly business report highlighting our company's growth in the technology sector, focusing on innovation, market expansion, and financial performance.",
        "length": 1500,
        "document_type": "formal",
        "statistics": json.dumps([
            {
                "name": "Revenue Growth",
                "value": 32.5,
                "unit": "%",
                "visualization_type": "bar"
            },
            {
                "name": "Customer Satisfaction",
                "value": 4.7,
                "unit": "/5",
                "visualization_type": "gauge"
            },
            {
                "name": "Market Share",
                "value": 18.3,
                "unit": "%",
                "visualization_type": "pie"
            }
        ]),
        "design_spec": json.dumps({
            "background_color": "#FFFFFF",
            "foreground_color_1": "#2563EB",
            "foreground_color_2": "#06B6D4",
            "theme_name": "Ocean Blue"
        })
    }

    try:
        print("\n📤 Sending request for formal document...")
        response = requests.post(f"{BASE_URL}/generate/document", data=payload)
        response.raise_for_status()

        result = response.json()
        job_id = result["job_id"]
        print(f"✅ Job created: {job_id}")
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        print(f"   Estimated time: {result['estimated_time_seconds']}s")

        return job_id

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"   Response: {e.response.text}")
        return None


def test_infographic_document():
    """Test infographic document generation"""
    print("\n" + "="*60)
    print("Testing INFOGRAPHIC Document Generation")
    print("="*60)

    payload = {
        "description": "Create an engaging annual report showcasing our company's achievements, growth trajectory, and key performance indicators for the year.",
        "length": 1500,
        "document_type": "infographic",
        "statistics": json.dumps([
            {
                "name": "Annual Revenue",
                "value": 25.8,
                "unit": "M USD",
                "visualization_type": "line"
            },
            {
                "name": "Employee Growth",
                "value": 145,
                "unit": "employees",
                "visualization_type": "bar"
            },
            {
                "name": "Customer Retention",
                "value": 94.2,
                "unit": "%",
                "visualization_type": "gauge"
            }
        ]),
        "design_spec": json.dumps({
            "background_color": "#FFFFFF",
            "foreground_color_1": "#DC2626",
            "foreground_color_2": "#FB923C",
            "theme_name": "Corporate Red"
        })
    }

    try:
        print("\n📤 Sending request for infographic document...")
        response = requests.post(f"{BASE_URL}/generate/document", data=payload)
        response.raise_for_status()

        result = response.json()
        job_id = result["job_id"]
        print(f"✅ Job created: {job_id}")
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        print(f"   Estimated time: {result['estimated_time_seconds']}s")

        return job_id

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"   Response: {e.response.text}")
        return None


def check_status(job_id, document_type):
    """Check job status and wait for completion"""
    print(f"\n⏳ Monitoring {document_type} document generation...")

    max_wait = 300  # 5 minutes max
    start_time = time.time()
    last_progress = 0

    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{BASE_URL}/generate/status/{job_id}")
            response.raise_for_status()

            status = response.json()

            # Show progress if it changed
            if status["progress"] != last_progress:
                print(f"   Progress: {status['progress']}% - {status['current_step']}")
                last_progress = status["progress"]

            if status["status"] == "completed":
                print(f"\n✅ {document_type} document generation completed!")
                print(f"   Document ID: {status['document_id']}")
                print(f"   Total time: {int(time.time() - start_time)}s")
                return True

            elif status["status"] == "failed":
                print(f"\n❌ {document_type} document generation failed!")
                print(f"   Error: {status.get('error_message', 'Unknown error')}")
                return False

            time.sleep(5)  # Check every 5 seconds

        except requests.exceptions.RequestException as e:
            print(f"❌ Error checking status: {str(e)}")
            return False

    print(f"\n⚠️ Timeout waiting for {document_type} document generation")
    return False


def download_document(job_id, document_type):
    """Download the generated document"""
    try:
        print(f"\n📥 Downloading {document_type} document...")
        response = requests.get(f"{BASE_URL}/generate/download/{job_id}")
        response.raise_for_status()

        filename = f"{document_type}_document.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)

        print(f"✅ Document saved as: {filename}")
        print(f"   File size: {len(response.content) / 1024:.2f} KB")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading: {str(e)}")
        return False


def test_invalid_document_type():
    """Test with invalid document type"""
    print("\n" + "="*60)
    print("Testing INVALID Document Type (should fail)")
    print("="*60)

    payload = {
        "description": "Test document",
        "length": 1000,
        "document_type": "invalid_type",  # Invalid!
        "statistics": json.dumps([]),
        "design_spec": json.dumps({
            "foreground_color_1": "#2563EB",
            "foreground_color_2": "#06B6D4"
        })
    }

    try:
        response = requests.post(f"{BASE_URL}/generate/document", data=payload)
        if response.status_code == 400:
            print("✅ Correctly rejected invalid document type")
            print(f"   Error message: {response.json()['detail']}")
        else:
            print("❌ Should have rejected invalid document type!")
    except requests.exceptions.RequestException as e:
        print(f"✅ Correctly rejected: {str(e)}")


def main():
    """Main test function"""
    print("\n" + "="*60)
    print("Document Type Test Suite")
    print("="*60)
    print("\nThis script will test:")
    print("1. Formal document generation")
    print("2. Infographic document generation")
    print("3. Invalid document type handling")
    print("\nMake sure the backend server is running!")
    print("="*60)

    input("\nPress Enter to continue...")

    # Test invalid type first
    test_invalid_document_type()

    # Test formal document
    formal_job_id = test_formal_document()
    if formal_job_id:
        if check_status(formal_job_id, "formal"):
            download_document(formal_job_id, "formal")

    # Wait a bit before next test
    print("\n⏸️  Waiting 10 seconds before next test...")
    time.sleep(10)

    # Test infographic document
    infographic_job_id = test_infographic_document()
    if infographic_job_id:
        if check_status(infographic_job_id, "infographic"):
            download_document(infographic_job_id, "infographic")

    print("\n" + "="*60)
    print("Test Suite Completed!")
    print("="*60)
    print("\n📊 Summary:")
    print("- Check the generated PDF files in this directory")
    print("- Review logs in backend/logs/ for detailed information")
    print("- Formal documents should be text-only")
    print("- Infographic documents should have images and charts")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
