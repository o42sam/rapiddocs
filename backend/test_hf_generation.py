#!/usr/bin/env python3
"""
Test script for Hugging Face text generation
"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("HUGGINGFACE_API_KEY")
MODEL = os.getenv("TEXT_GENERATION_MODEL", "meta-llama/Llama-3.2-3B-Instruct")

def test_hf_api():
    """Test Hugging Face API connection and text generation"""

    print(f"Testing Hugging Face API")
    print(f"Model: {MODEL}")
    print(f"API Key: {API_KEY[:10]}..." if API_KEY else "No API Key")
    print("-" * 60)

    # Test URL
    api_url = f"https://api-inference.huggingface.co/models/{MODEL}"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    # Simple test prompt
    payload = {
        "inputs": "Write a short professional business document about sustainable investing. Target: 200 words.",
        "parameters": {
            "temperature": 0.7,
            "top_p": 0.95,
            "max_new_tokens": 300,
            "return_full_text": False,
            "do_sample": True,
        }
    }

    print(f"Sending request to: {api_url}")
    print(f"Payload: {payload}")
    print("-" * 60)

    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=120
        )

        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("-" * 60)

        if response.status_code == 200:
            result = response.json()
            print(f"Response Type: {type(result)}")
            print(f"Response Content: {result}")
            print("-" * 60)

            # Extract generated text
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                print(f"✅ SUCCESS!")
                print(f"Generated Text ({len(generated_text.split())} words):")
                print(generated_text)
                return True
            elif isinstance(result, dict):
                generated_text = result.get("generated_text", "")
                print(f"✅ SUCCESS!")
                print(f"Generated Text ({len(generated_text.split())} words):")
                print(generated_text)
                return True
            else:
                print(f"❌ Unexpected response format: {result}")
                return False
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hf_api()
    exit(0 if success else 1)
