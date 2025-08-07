import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app

client = TestClient(app)

class TestAPI:
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Credit Risk Prediction API" in response.json()["message"]
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_model_info_endpoint(self):
        """Test model info endpoint"""
        response = client.get("/model/info")
        assert response.status_code == 200
        assert "model_name" in response.json()
    
    def test_predict_endpoint(self):
        """Test prediction endpoint"""
        test_data = {
            "Income": 75000,
            "Age": 35,
            "LoanAmount": 200000,
            "CreditScore": 750,
            "DebtToIncome": 0.25,
            "EmploymentYears": 8,
            "LoanTerm": 30
        }
        
        response = client.post("/predict", json=test_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "prediction" in result
        assert "probability" in result
        assert "risk_score" in result
        assert result["prediction"] in ["low_risk", "high_risk"]
    
    def test_batch_predict_endpoint(self):
        """Test batch prediction endpoint"""
        test_data = [
            {
                "Income": 75000,
                "Age": 35,
                "LoanAmount": 200000,
                "CreditScore": 750,
                "DebtToIncome": 0.25,
                "EmploymentYears": 8,
                "LoanTerm": 30
            },
            {
                "Income": 25000,
                "Age": 22,
                "LoanAmount": 300000,
                "CreditScore": 500,
                "DebtToIncome": 0.8,
                "EmploymentYears": 1,
                "LoanTerm": 15
            }
        ]
        
        response = client.post("/predict/batch", json=test_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "predictions" in result
        assert len(result["predictions"]) == 2
