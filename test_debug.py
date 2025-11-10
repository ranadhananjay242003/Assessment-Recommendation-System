from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

# Test health
r = client.get('/health')
print(f"Health: {r.status_code} {r.json()}")

# Test recommend with error details
r = client.post('/recommend', json={"query": "test"})
print(f"\nRecommend: {r.status_code}")
print(f"Response: {r.json()}")

