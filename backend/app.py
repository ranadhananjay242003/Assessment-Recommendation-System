# backend/app.py

from typing import Dict
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

# This dictionary will safely hold our model instance after it's loaded.
model_storage: Dict = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This function handles the application's startup.
    It loads the REAL recommender model when the app starts.
    """
    print("Lifespan event: Loading REAL Recommender model...")
    try:
        from backend.recommender import Recommender
        model_storage["recommender"] = Recommender()
        print("Lifespan event: REAL Recommender model loaded successfully.")
    except Exception as e:
        import traceback
        print("--- LIFESPAN ERROR: FAILED TO LOAD RECOMMENDER ---")
        traceback.print_exc()
        print("-------------------------------------------------")
    
    yield  # The application is now running.
    
    print("Lifespan event: Shutting down and clearing resources.")
    model_storage.clear()

app = FastAPI(
    title="SHL Assessment Recommender",
    version="1.0.0",
    lifespan=lifespan
)

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "https://assessment-recommendation-system-six.vercel.app", 
    "http://127.0.0.1:5500"
    "http://localhost:3000" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        raise HTTPException(status_code=503, detail="Recommender model is not available or failed to load.")
    
    results = recommender.recommend(req.query.strip(), top_k=10)
    return {"recommended_assessments": results}
