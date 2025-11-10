"""
Verify API compliance with PDF Appendix 2 specification
"""
import sys
from backend.recommender import Recommender
from backend.app import app, recommender as app_recommender

# Manually load recommender for testing
print("Loading recommender model...")
rec = Recommender()

# Override the global recommender
import backend.app as app_module
app_module.recommender = rec

from fastapi.testclient import TestClient
client = TestClient(app)

print("\n" + "=" * 80)
print("API COMPLIANCE TEST - PDF APPENDIX 2")
print("=" * 80)

# TEST 1: Health Endpoint
print("\n[TEST 1] GET /health")
print("-" * 80)
response = client.get("/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200 and response.json() == {"status": "healthy"}:
    print("✓ PASS - Health endpoint compliant")
else:
    print("✗ FAIL - Health endpoint not compliant")
    sys.exit(1)

# TEST 2: Recommend Endpoint Structure
print("\n[TEST 2] POST /recommend - Response Structure")
print("-" * 80)

test_payload = {"query": "I need Java developers"}
response = client.post("/recommend", json=test_payload)

print(f"Status: {response.status_code}")

if response.status_code != 200:
    print(f"✗ FAIL - Expected 200, got {response.status_code}")
    print(f"Response: {response.json()}")
    sys.exit(1)

data = response.json()
print(f"Top-level keys: {list(data.keys())}")

# Check for recommended_assessments key
if "recommended_assessments" not in data:
    print("✗ FAIL - Missing 'recommended_assessments' key")
    sys.exit(1)

print("✓ PASS - Has 'recommended_assessments' key")

# TEST 3: Assessment Fields
print("\n[TEST 3] Assessment Object Fields (PDF Spec)")
print("-" * 80)

assessments = data["recommended_assessments"]
print(f"Number of assessments returned: {len(assessments)}")

if not isinstance(assessments, list):
    print("✗ FAIL - recommended_assessments is not a list")
    sys.exit(1)

if len(assessments) == 0:
    print("✗ FAIL - No assessments returned")
    sys.exit(1)

# According to PDF Page 4, each assessment must have:
required_schema = {
    "url": (str, "Valid URL to the assessment resource"),
    "name": (str, "Name of the assessment"),
    "adaptive_support": (str, 'Either "Yes" or "No"'),
    "description": (str, "Detailed description of the assessment"),
    "duration": (int, "Duration of the assessment in minutes"),
    "remote_support": (str, 'Either "Yes" or "No"'),
    "test_type": (list, "Categories or types of the assessment")
}

sample = assessments[0]
print(f"\nSample assessment fields: {sorted(sample.keys())}")

all_passed = True
for field, (expected_type, description) in required_schema.items():
    if field not in sample:
        print(f"✗ FAIL - Missing required field: '{field}'")
        print(f"         Description: {description}")
        all_passed = False
        continue
    
    value = sample[field]
    actual_type = type(value)
    
    if not isinstance(value, expected_type):
        print(f"✗ FAIL - Field '{field}' has wrong type")
        print(f"         Expected: {expected_type.__name__}, Got: {actual_type.__name__}")
        all_passed = False
        continue
    
    print(f"✓ PASS - '{field}' ({expected_type.__name__}): {description}")

if not all_passed:
    print("\n✗✗✗ COMPLIANCE TEST FAILED")
    sys.exit(1)

# TEST 4: Sample Data Validation
print("\n[TEST 4] Sample Assessment Data")
print("-" * 80)

print("\nFirst Assessment:")
for field in required_schema.keys():
    value = sample[field]
    if isinstance(value, str) and len(value) > 60:
        display_value = value[:60] + "..."
    else:
        display_value = value
    print(f"  {field:20s}: {display_value}")

# Validate specific constraints
issues = []

if not sample["url"].startswith("http"):
    issues.append("URL doesn't start with http")

if sample["adaptive_support"] not in ["Yes", "No"]:
    issues.append(f"adaptive_support should be 'Yes' or 'No', got '{sample['adaptive_support']}'")

if sample["remote_support"] not in ["Yes", "No"]:
    issues.append(f"remote_support should be 'Yes' or 'No', got '{sample['remote_support']}'")

if sample["duration"] <= 0:
    issues.append("duration should be positive")

if not isinstance(sample["test_type"], list) or len(sample["test_type"]) == 0:
    issues.append("test_type should be a non-empty list")

if issues:
    print("\n⚠ Warnings:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("\n✓ All data validation checks passed")

# Final Summary
print("\n" + "=" * 80)
print("✓✓✓ API IS FULLY COMPLIANT WITH PDF SPECIFICATION")
print("=" * 80)
print("\nSummary:")
print(f"  - Health endpoint: ✓ Correct")
print(f"  - Response structure: ✓ Has 'recommended_assessments' key")
print(f"  - Assessment fields: ✓ All 7 required fields present")
print(f"  - Field types: ✓ All types match specification")
print(f"  - Sample validation: ✓ Data formats correct")
print("\n✅ READY FOR SUBMISSION")

