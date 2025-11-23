"""
Test script for fraud detection pipeline
Run this to verify everything works end-to-end
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_service_level.profile_agent import ProfileAgent
from ai_service_level.fraud_agent import FraudAgent

# Test partner_id (from the data)
TEST_PARTNER_ID = "96a660ff-08e0-49c1-be6d-bb22a84e742e"

def test_profile_agent():
    """Test Step 1: Profile Agent data extraction"""
    print("=" * 60)
    print("TEST 1: Profile Agent - Data Extraction")
    print("=" * 60)
    
    try:
        profile_agent = ProfileAgent(data_dir="data")
        profile_text = profile_agent.get_profile_text(TEST_PARTNER_ID)
        
        print("✅ Profile Agent works!")
        print(f"\nExtracted profile text length: {len(profile_text)} characters")
        print("\nFirst 500 characters:")
        print(profile_text[:500])
        print("...")
        
        return True
    except Exception as e:
        print(f"❌ Profile Agent failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llama_connection():
    """Test Step 2: LLaMA server connection"""
    print("\n" + "=" * 60)
    print("TEST 2: LLaMA Server Connection")
    print("=" * 60)
    
    try:
        from ai_service_level.llama_client import LlamaClient
        
        client = LlamaClient(base_url="http://127.0.0.1:8080")
        result = client.generate(
            prompt="Say 'Hello, fraud detection system is working!'",
            system_message="You are a helpful assistant.",
            max_tokens=50
        )
        
        print("✅ LLaMA connection works!")
        print(f"Response: {result['content']}")
        return True
    except Exception as e:
        print(f"❌ LLaMA connection failed: {e}")
        print("\nMake sure llama-server is running:")
        print("./build/bin/llama-server -m model.gguf --port 8080")
        return False

def test_fraud_agent():
    """Test Step 3: Full Fraud Agent pipeline"""
    print("\n" + "=" * 60)
    print("TEST 3: Fraud Agent - Full Pipeline")
    print("=" * 60)
    
    try:
        fraud_agent = FraudAgent(data_dir="data", llama_url="http://127.0.0.1:8080")
        result = fraud_agent.assess_risk(TEST_PARTNER_ID)
        
        print("✅ Fraud Agent works!")
        print(f"\nPartner ID: {result['partner_id']}")
        print(f"Risk Score: {result['risk_score']}/100")
        print(f"\nRationale:")
        print(result['rationale'])
        
        return True
    except Exception as e:
        print(f"❌ Fraud Agent failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_api():
    """Test Step 4: Backend API (if backend is running)"""
    print("\n" + "=" * 60)
    print("TEST 4: Backend API")
    print("=" * 60)
    
    try:
        import requests
        
        response = requests.post(
            "http://localhost:5000/api/assess-risk",
            json={"partner_id": TEST_PARTNER_ID},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend API works!")
            print(f"Risk Score: {data['risk_score']}/100")
            print(f"Rationale: {data['rationale'][:200]}...")
            return True
        else:
            print(f"❌ Backend returned error: {response.status_code}")
            print(response.text)
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  Backend not running. Start it with: python backend/app.py")
        return None
    except Exception as e:
        print(f"❌ Backend API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("FRAUD DETECTION PIPELINE TEST")
    print("=" * 60)
    print(f"\nTesting with partner_id: {TEST_PARTNER_ID}\n")
    
    results = {}
    
    # Test 1: Profile Agent
    results['profile'] = test_profile_agent()
    
    # Test 2: LLaMA Connection
    results['llama'] = test_llama_connection()
    
    # Test 3: Fraud Agent (only if previous tests passed)
    if results['profile'] and results['llama']:
        results['fraud'] = test_fraud_agent()
    else:
        print("\n⚠️  Skipping Fraud Agent test (prerequisites failed)")
        results['fraud'] = False
    
    # Test 4: Backend API (optional)
    results['backend'] = test_backend_api()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Profile Agent: {'✅ PASS' if results['profile'] else '❌ FAIL'}")
    print(f"LLaMA Connection: {'✅ PASS' if results['llama'] else '❌ FAIL'}")
    print(f"Fraud Agent: {'✅ PASS' if results.get('fraud') else '❌ FAIL'}")
    if results['backend'] is not None:
        print(f"Backend API: {'✅ PASS' if results['backend'] else '❌ FAIL'}")
    else:
        print(f"Backend API: ⚠️  NOT TESTED (backend not running)")
    
    if all([results['profile'], results['llama'], results.get('fraud')]):
        print("\n🎉 All core tests passed! Your fraud detection system is working!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()

# debugger duck quest
