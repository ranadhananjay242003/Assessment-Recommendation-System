from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from .recommender import Recommender
except ImportError:
    from recommender import Recommender

app = FastAPI(title="SHL Assessment Recommender", version="1.0.0")

# Allow local static frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendRequest(BaseModel):
    query: str = Field(..., description="User's free-text query or JD")


class AssessmentOut(BaseModel):
    url: str
    name: str
    adaptive_support: str
    description: str
    duration: int
    remote_support: str
    test_type: List[str]


recommender: Optional[Recommender] = None


@app.on_event("startup")
def _load_recommender():
    global recommender
    recommender = Recommender()


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/recommend")
async def recommend(req: RecommendRequest):
    if recommender is None:
        raise HTTPException(status_code=503, detail="Model not ready")
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Empty query")
    try:
        results = recommender.recommend(req.query.strip(), top_k=10)
        # Return in the format specified in the API spec
        return {"recommended_assessments": results}
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Data missing: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

