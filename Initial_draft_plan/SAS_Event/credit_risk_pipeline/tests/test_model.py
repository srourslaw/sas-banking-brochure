import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import predict_credit_risk, model_loader

class TestCreditRiskModel:
    
    def test_model_loading(self):
        """Test that model artifacts are loaded correctly"""
        assert len(model_loader.coefficients) > 0
        assert 'Intercept' in model_loader.coefficients
        assert model_loader.metadata is not None
    
    def test_prediction_low_risk(self):
        """Test prediction for low risk profile"""
        features = {
            'Income': 75000,
            'Age': 35,
            'LoanAmount': 200000,
            'CreditScore': 750,
            'DebtToIncome': 0.25,
            'EmploymentYears': 8,
            'LoanTerm': 30
        }
        
        result = predict_credit_risk(features)
        
        assert 'prediction' in result
        assert 'probability' in result
        assert 'risk_score' in result
        assert result['prediction'] in ['low_risk', 'high_risk']
        assert 0 <= result['probability'] <= 1
        assert 0 <= result['risk_score'] <= 100
    
    def test_prediction_high_risk(self):
        """Test prediction for high risk profile"""
        features = {
            'Income': 25000,
            'Age': 22,
            'LoanAmount': 300000,
            'CreditScore': 500,
            'DebtToIncome': 0.8,
            'EmploymentYears': 1,
            'LoanTerm': 15
        }
        
        result = predict_credit_risk(features)
        
        assert 'prediction' in result
        assert 'probability' in result
        assert 'risk_score' in result
        assert result['prediction'] in ['low_risk', 'high_risk']
        assert 0 <= result['probability'] <= 1
        assert 0 <= result['risk_score'] <= 100

    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test with zero values
        features = {
            'Income': 0,
            'Age': 18,
            'LoanAmount': 0,
            'CreditScore': 300,
            'DebtToIncome': 0,
            'EmploymentYears': 0,
            'LoanTerm': 10
        }
        
        result = predict_credit_risk(features)
        assert result is not None
        assert 'prediction' in result
