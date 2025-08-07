import os
import json
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import logging
from datetime import datetime
from prometheus_fastapi_instrumentator import Instrumentator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Credit Risk Prediction API",
    description="Real-time credit risk assessment using ML model",
    version="1.0.0"
)

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Load model coefficients and metadata
class ModelLoader:
    def __init__(self):
        self.coefficients = {}
        self.metadata = {}
        self.load_model_artifacts()
    
    def load_model_artifacts(self):
        try:
            # Load coefficients
            coeff_path = "model_artifact/model_coefficients.txt"
            with open(coeff_path, 'r') as f:
                for line in f:
                    if line.strip():
                        var, coeff = line.strip().split(',')
                        self.coefficients[var] = float(coeff)
            
            # Load metadata
            meta_path = "model_artifact/model_metadata.json"
            with open(meta_path, 'r') as f:
                self.metadata = json.load(f)
                
            logger.info(f"Model loaded successfully: {self.metadata['model_name']}")
            
        except Exception as e:
            logger.error(f"Error loading model artifacts: {e}")
            raise

# Initialize model
model_loader = ModelLoader()

# Request/Response models
class PredictionRequest(BaseModel):
    Income: float
    Age: int
    LoanAmount: float
    CreditScore: int
    DebtToIncome: float
    EmploymentYears: int
    LoanTerm: int

class PredictionResponse(BaseModel):
    prediction: str
    probability: float
    risk_score: float
    model_version: str
    timestamp: str

# Prediction function
def predict_credit_risk(features: Dict[str, float]) -> Dict[str, Any]:
    try:
        # Calculate linear combination
        linear_combo = model_loader.coefficients.get('Intercept', 0)
        
        for feature, value in features.items():
            if feature in model_loader.coefficients:
                linear_combo += model_loader.coefficients[feature] * value
        
        # Apply sigmoid function
        probability = 1 / (1 + np.exp(-linear_combo))
        
        # Determine prediction
        prediction = "high_risk" if probability > 0.5 else "low_risk"
        
        return {
            "prediction": prediction,
            "probability": round(probability, 4),
            "risk_score": round(probability * 100, 2),
            "model_version": model_loader.metadata.get("model_version", "1.0.0"),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

# API Endpoints
@app.get("/")
async def demo_interface():
    """Serve the enhanced demo interface for mobile users"""
    return FileResponse("src/demo_interface_enhanced.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/model/info")
async def model_info():
    return model_loader.metadata

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    features = request.dict()
    result = predict_credit_risk(features)
    return PredictionResponse(**result)

@app.post("/predict/batch")
async def predict_batch(requests: List[PredictionRequest]):
    results = []
    for req in requests:
        features = req.dict()
        result = predict_credit_risk(features)
        results.append(result)
    return {"predictions": results}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
