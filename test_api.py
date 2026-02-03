"""
API Test Script - Test all endpoints and model functionality
"""

import requests
import json
import sys
import time
import subprocess
import os
import signal

def start_api_server():
    """Start API server in background"""
    print("=" * 80)
    print("STARTING API SERVER")
    print("=" * 80)
    
    # Start server
    process = subprocess.Popen(
        ["python", "-m", "uvicorn", "api.inference_api:app", "--host", "127.0.0.1", "--port", "8002"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait for startup
    print("Waiting for server to start...")
    time.sleep(5)
    
    return process

def test_health_endpoint(base_url):
    """Test /health endpoint"""
    print("\n" + "=" * 80)
    print("TEST 1: Health Check Endpoint")
    print("=" * 80)
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Health check passed!")
            print(f"   Status: {data.get('status')}")
            print(f"   Model Loaded: {data.get('model_loaded')}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_root_endpoint(base_url):
    """Test / root endpoint"""
    print("\n" + "=" * 80)
    print("TEST 2: Root Endpoint")
    print("=" * 80)
    
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Root endpoint working!")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_predict_endpoint(base_url):
    """Test /predict endpoint"""
    print("\n" + "=" * 80)
    print("TEST 3: Prediction Endpoint")
    print("=" * 80)
    
    # Test data
    test_applicant = {
        "applicant_id": "TEST001",
        "age": 35,
        "annual_income": 75000,
        "credit_score": 720,
        "debt_to_income_ratio": 0.35
    }
    
    print(f"Input Data:")
    print(json.dumps(test_applicant, indent=2))
    
    try:
        response = requests.post(
            f"{base_url}/predict",
            json=test_applicant,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Prediction successful!")
            print(f"\nPrediction Results:")
            print(f"   Applicant ID: {result.get('applicant_id')}")
            print(f"   Risk Score: {result.get('risk_score')}")
            print(f"   Risk Category: {result.get('risk_category')}")
            print(f"   Decision: {result.get('decision')}")
            print(f"   Reason Codes:")
            for reason in result.get('reason_codes', []):
                print(f"      - {reason}")
            print(f"   Timestamp: {result.get('timestamp')}")
            
            # Validate response structure
            assert 'applicant_id' in result, "Missing applicant_id"
            assert 'risk_score' in result, "Missing risk_score"
            assert 'risk_category' in result, "Missing risk_category"
            assert 'decision' in result, "Missing decision"
            assert 'reason_codes' in result, "Missing reason_codes"
            
            print("\n✅ All response fields present!")
            return True
        else:
            print(f"❌ Prediction failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_info_endpoint(base_url):
    """Test /model/info endpoint"""
    print("\n" + "=" * 80)
    print("TEST 4: Model Info Endpoint")
    print("=" * 80)
    
    try:
        response = requests.get(f"{base_url}/model/info", timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            info = response.json()
            print(f"\n✅ Model info retrieved!")
            print(f"\nModel Information:")
            print(f"   Model Type: {info.get('model_type')}")
            print(f"   Version: {info.get('version')}")
            print(f"   Training Date: {info.get('training_date')}")
            print(f"   Features: {info.get('features')}")
            print(f"\n   Performance Metrics:")
            for key, value in info.get('performance', {}).items():
                print(f"      {key}: {value}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_multiple_predictions(base_url):
    """Test multiple predictions with different profiles"""
    print("\n" + "=" * 80)
    print("TEST 5: Multiple Prediction Scenarios")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "Low Risk Profile",
            "data": {
                "applicant_id": "LOW_RISK_001",
                "age": 40,
                "annual_income": 120000,
                "credit_score": 800,
                "debt_to_income_ratio": 0.15
            }
        },
        {
            "name": "Medium Risk Profile",
            "data": {
                "applicant_id": "MED_RISK_001",
                "age": 28,
                "annual_income": 50000,
                "credit_score": 650,
                "debt_to_income_ratio": 0.40
            }
        },
        {
            "name": "High Risk Profile",
            "data": {
                "applicant_id": "HIGH_RISK_001",
                "age": 22,
                "annual_income": 30000,
                "credit_score": 550,
                "debt_to_income_ratio": 0.55
            }
        }
    ]
    
    results = []
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        print(f"   Credit Score: {test_case['data']['credit_score']}")
        print(f"   Income: ${test_case['data']['annual_income']:,}")
        print(f"   DTI: {test_case['data']['debt_to_income_ratio']:.1%}")
        
        try:
            response = requests.post(
                f"{base_url}/predict",
                json=test_case['data'],
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   → Risk Score: {result['risk_score']}")
                print(f"   → Category: {result['risk_category']}")
                print(f"   → Decision: {result['decision']}")
                results.append(True)
            else:
                print(f"   ❌ Failed: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n{'='*80}")
    print(f"Success Rate: {success_rate:.0f}% ({sum(results)}/{len(results)} tests passed)")
    
    return all(results)

def main():
    """Run all API tests"""
    print("\n" + "=" * 80)
    print("CREDIT RISK SCORING API - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    base_url = "http://127.0.0.1:8002"
    process = None
    
    try:
        # Start API server
        process = start_api_server()
        
        # Check if server started
        print("\nChecking server availability...")
        for i in range(3):
            try:
                response = requests.get(f"{base_url}/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Server is ready!")
                    break
            except:
                print(f"Attempt {i+1}/3: Server not ready yet...")
                time.sleep(2)
        else:
            print("❌ Server failed to start")
            return
        
        # Run tests
        results = {}
        results['health'] = test_health_endpoint(base_url)
        results['root'] = test_root_endpoint(base_url)
        results['predict'] = test_predict_endpoint(base_url)
        results['model_info'] = test_model_info_endpoint(base_url)
        results['multiple'] = test_multiple_predictions(base_url)
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_name.upper():20s} : {status}")
        
        total_passed = sum(results.values())
        total_tests = len(results)
        
        print("=" * 80)
        print(f"TOTAL: {total_passed}/{total_tests} tests passed ({total_passed/total_tests*100:.0f}%)")
        print("=" * 80)
        
        if total_passed == total_tests:
            print("\n🎉 ALL TESTS PASSED! API is working perfectly! 🎉\n")
        else:
            print(f"\n⚠️  {total_tests - total_passed} test(s) failed\n")
            
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        
    finally:
        # Cleanup
        if process:
            print("\nStopping API server...")
            process.terminate()
            time.sleep(2)
            if process.poll() is None:
                process.kill()
            print("✅ Server stopped")

if __name__ == "__main__":
    main()
