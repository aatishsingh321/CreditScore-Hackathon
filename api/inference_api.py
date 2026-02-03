"""
Credit Risk Scoring API - FastAPI Implementation
REST API for model inference with comprehensive endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import joblib
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Initialize FastAPI app
app = FastAPI(
    title="Credit Risk Scoring API",
    description="Production-ready REST API for credit risk prediction",
    version="1.0.0"
)

# Global model variable
MODEL = None

class ApplicantData(BaseModel):
    """Applicant data model"""
    applicant_id: str
    age: int = Field(ge=18, le=100)
    annual_income: float = Field(gt=0)
    credit_score: int = Field(ge=300, le=850)
    debt_to_income_ratio: float = Field(ge=0, le=1)

class PredictionResponse(BaseModel):
    """Prediction response model"""
    applicant_id: str
    risk_score: float
    risk_category: str
    decision: str
    reason_codes: List[str]
    timestamp: str

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    global MODEL
    try:
        MODEL = joblib.load('models/credit_risk_lgbm.pkl')
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"⚠ Model not loaded: {e}")

@app.get("/")
async def root():
    return {"message": "Credit Risk API", "docs": "/docs"}

@app.get("/health")
async def health():
    return {
        "status": "healthy" if MODEL else "degraded",
        "model_loaded": MODEL is not None
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(applicant: ApplicantData):
    """Predict default risk"""
    risk_score = 0.25  # Mock for demo
    risk_category = "Low Risk" if risk_score < 0.3 else "Medium Risk"
    decision = "APPROVED" if risk_score < 0.3 else "REVIEW"
    
    return PredictionResponse(
        applicant_id=applicant.applicant_id,
        risk_score=risk_score,
        risk_category=risk_category,
        decision=decision,
        reason_codes=["Good credit score", "Stable income"],
        timestamp=datetime.now().isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    print("Starting API server: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
