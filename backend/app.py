# backend/app.py

from typing import Dict, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# This dictionary will hold our recommender instance.
model_storage: Dict = {}

# --- A 100% SAFE, PURE PYTHON DUMMY RECOMMENDER ---
# It has no external dependencies like pandas or sentence-transformers.
class DummyRecommender:
    def recommend(self, query: str, top_k: int = 10) -> List[Dict]:
        print(f"DummyRecommender received query: '{query}'")
        # We return a hardcoded, valid list of assessments.
        # This proves the entire API request/response cycle is working.
        return [
            {
                "url": "http://example.com/test/1",
                "name": f"Dummy Assessment for '{query}'",
                "adaptive_support": "No",
                "description": "This is a dummy response to prove the API is working.",
                "duration": 30,
                "remote_support": "Yes",
                "test_type": ["Dummy", "Proof of Concept"]
            }
        ]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This lifespan function is guaranteed to work because it only
    loads the safe DummyRecommender.
    """
    print("Lifespan event: Loading DUMMY Recommender model...")
    # We are NOT using the real recommender. This is the key to the test.
    model_storage["recommender"] = DummyRecommender()
    print("Lifespan event: DUMMY Recommender model loaded successfully.")
    
    yield
    
    print("Lifespan event: Shutting down and clearing resources.")
    model_storage.clear()

app = FastAPI(
    title="SHL Assessment Recommender (DIAGNOSTIC MODE)",
    version="1.0.0",
    lifespan=lifespan
)

class RecommendRequest(BaseModel):
    query: str = Field(..., description="User's free-text query or JD")

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/recommend")
async def recommend(req: RecommendRequest):
    recommender = model_storage.get("recommender")
    if not recommender:
        raise HTTPException(status_code=503, detail="Recommender model is not available.")
    
    results = recommender.recommend(req.query.strip(), top_k=10)
    return {"recommended_assessments": results}
