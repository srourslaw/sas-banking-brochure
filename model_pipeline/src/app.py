import os
import json
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import uvicorn
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SAS Credit Risk Prediction API",
    description="Real-time credit risk assessment using SAS Model Studio models",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SAS Model Loading ---
class SASModelLoader:
    def __init__(self):
        self.coefficients = {}
        self.metadata = {}
        self.model_ready = False
        self.load_sas_model()

    def load_sas_model(self):
        """Load SAS model coefficients and metadata from /app/model_artifact"""
        try:
            coeff_path = "model_artifact/model_coefficients.json"
            meta_path = "model_artifact/deployment_config.json"

            if os.path.exists(coeff_path) and os.path.exists(meta_path):
                with open(coeff_path, 'r') as f:
                    model_data = json.load(f)
                self.coefficients = model_data.get('coefficients', {})
                
                with open(meta_path, 'r') as f:
                    self.metadata = json.load(f)
                
                self.model_ready = len(self.coefficients) > 0
                if self.model_ready:
                    logger.info(f"✅ SAS model '{self.metadata.get('model_name')}' loaded successfully.")
            else:
                logger.warning("⚠️ SAS model artifacts not found. Loading fallback model.")
                self._load_fallback_model()
        except Exception as e:
            logger.error(f"❌ Error loading SAS model: {e}")
            self._load_fallback_model()

    def _load_fallback_model(self):
        """Fallback model for demo purposes"""
        self.coefficients = {"Intercept": 0, "Fallback": 1}
        self.metadata = {"model_name": "Fallback Model"}
        self.model_ready = True

sas_model = SASModelLoader()

# --- Pydantic Models ---
class CreditRiskRequest(BaseModel):
    Income: float = Field(..., example=75000)
    Age: int = Field(..., example=35)
    LoanAmount: float = Field(..., example=200000)
    CreditScore: int = Field(..., example=750)
    DebtToIncome: float = Field(..., example=0.25)
    EmploymentYears: int = Field(..., example=8)
    LoanTerm: int = Field(..., example=30)

class CreditRiskResponse(BaseModel):
    prediction: str
    risk_probability: float
    model_version: str
    model_name: str

# --- API Endpoints ---
@app.get("/health")
async def health_check():
    """Returns the operational status and loaded model name."""
    return {
        "status": "healthy",
        "model_ready": sas_model.model_ready,
        "model_source": sas_model.metadata.get("model_name", "Unknown"),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/model/info")
async def get_model_info():
    """Returns detailed metadata and coefficient summary for the loaded model."""
    if not sas_model.model_ready:
        raise HTTPException(status_code=404, detail="Model not loaded")
    return {
        "metadata": sas_model.metadata,
        "coefficients": {
            "count": len(sas_model.coefficients),
            "names": list(sas_model.coefficients.keys())
        }
    }

@app.post("/predict", response_model=CreditRiskResponse)
async def predict_credit_risk(request: CreditRiskRequest):
    """Predicts credit risk based on input features."""
    if not sas_model.model_ready:
        raise HTTPException(status_code=503, detail="Model not ready for predictions")

    features = request.dict()
    linear_combo = sas_model.coefficients.get('Intercept', 0)
    for feature, value in features.items():
        if feature in sas_model.coefficients:
            linear_combo += sas_model.coefficients[feature] * value
    
    risk_probability = 1 / (1 + np.exp(-linear_combo))
    prediction = "high_risk" if risk_probability > 0.5 else "low_risk"

    return CreditRiskResponse(
        prediction=prediction,
        risk_probability=risk_probability,
        model_version=sas_model.metadata.get("model_version", "N/A"),
        model_name=sas_model.metadata.get("model_name", "N/A")
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
