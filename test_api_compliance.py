from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

print("=" * 80)
print("TESTING API COMPLIANCE WITH PDF SPECIFICATION")
print("=" * 80)

# Test 1: Health Check Endpoint
print("\n1. Testing GET /health")
print("-" * 80)
response = client.get('/health')
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

expected_health = {"status": "healthy"}
actual_health = response.json()

if response.status_code == 200 and actual_health == expected_health:
    print("✓ PASS: Health endpoint matches spec")
else:
    print("✗ FAIL: Health endpoint doesn't match spec")

# Test 2: Recommendation Endpoint
print("\n2. Testing POST /recommend")
print("-" * 80)

test_query = "JD/query in string"
payload = {"query": test_query}

response = client.post('/recommend', json=payload)
print(f"Status Code: {response.status_code}")
data = response.json()

print(f"\nResponse keys: {list(data.keys())}")

# According to PDF spec, response should have "recommended_assessments" key
if "recommended_assessments" in data:
    print("✓ PASS: Response has 'recommended_assessments' key")
    
    assessments = data["recommended_assessments"]
    print(f"Number of assessments: {len(assessments)}")
    
    if len(assessments) > 0:
        print("\n3. Checking Assessment Fields (PDF Appendix 2)")
        print("-" * 80)
        
        # Required fields according to PDF
        required_fields = {
            "url": str,
            "name": str, 
            "adaptive_support": str,
            "description": str,
            "duration": int,
            "remote_support": str,
            "test_type": list
        }
        
        sample = assessments[0]
        print(f"Sample assessment keys: {sorted(sample.keys())}")
        
        all_good = True
        for field, expected_type in required_fields.items():
            if field not in sample:
                print(f"✗ FAIL: Missing field '{field}'")
                all_good = False
            else:
                actual_type = type(sample[field])
                if not isinstance(sample[field], expected_type):
                    print(f"✗ FAIL: Field '{field}' has type {actual_type.__name__}, expected {expected_type.__name__}")
                    all_good = False
                else:
                    print(f"✓ PASS: Field '{field}' has correct type ({expected_type.__name__})")
        
        if all_good:
            print("\n✓✓✓ ALL CHECKS PASSED - API is compliant with PDF spec")
        else:
            print("\n✗✗✗ SOME CHECKS FAILED - API needs fixes")
            
        print("\nSample Assessment:")
        print("-" * 80)
        for key in required_fields.keys():
            value = sample.get(key)
            if isinstance(value, str) and len(value) > 80:
                value = value[:80] + "..."
            print(f"  {key}: {value}")
            
else:
    print("✗ FAIL: Response doesn't have 'recommended_assessments' key")
    print(f"Actual keys: {list(data.keys())}")

print("\n" + "=" * 80)
print("COMPLIANCE TEST COMPLETE")
print("=" * 80)

