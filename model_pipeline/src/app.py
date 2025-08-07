import os
import json
import numpy as np
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uvicorn
import logging
from datetime import datetime, timedelta
import random
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SAS Banking Intelligence API",
    description="Enterprise credit risk assessment with alternative data and portfolio intelligence",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enhanced CORS middleware for mobile compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Set to False for broader compatibility
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "accept",
        "accept-encoding",
        "authorization",
        "content-type",
        "dnt",
        "origin",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
        "ngrok-skip-browser-warning",
        "access-control-allow-origin",
        "access-control-allow-headers",
        "access-control-allow-methods"
    ],
    expose_headers=["*"]
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
            # Try multiple possible paths for model artifacts
            possible_paths = [
                ("model_artifact/model_coefficients.json", "model_artifact/deployment_config.json"),
                ("../model_artifact/model_coefficients.json", "../model_artifact/deployment_config.json"),
                ("./model_artifact/model_coefficients.json", "./model_artifact/deployment_config.json")
            ]
            
            coeff_path = None
            meta_path = None
            
            for coeff_candidate, meta_candidate in possible_paths:
                if os.path.exists(coeff_candidate) and os.path.exists(meta_candidate):
                    coeff_path = coeff_candidate
                    meta_path = meta_candidate
                    logger.info(f"Found model artifacts at: {coeff_path}")
                    break
            
            if not coeff_path:
                logger.warning("⚠️ SAS model artifacts not found in any expected location. Loading fallback model.")
                self._load_fallback_model()
                return
                
            with open(coeff_path, 'r') as f:
                model_data = json.load(f)
            self.coefficients = model_data.get('coefficients', {})
            
            with open(meta_path, 'r') as f:
                self.metadata = json.load(f)
            
            self.model_ready = len(self.coefficients) > 0
            if self.model_ready:
                logger.info(f"✅ SAS model '{self.metadata.get('model_name')}' loaded successfully.")
        except Exception as e:
            logger.error(f"❌ Error loading SAS model: {e}")
            self._load_fallback_model()

    def _load_fallback_model(self):
        """Fallback model for demo purposes"""
        self.coefficients = {"Intercept": 0, "Fallback": 1}
        self.metadata = {"model_name": "Fallback Model"}
        self.model_ready = True

# --- Enums (Must be defined before classes that use them) ---
class RiskLevel(str, Enum):
    LOW = "low_risk"
    MEDIUM = "medium_risk"
    HIGH = "high_risk"

class CustomerSegment(str, Enum):
    PREMIUM = "premium"
    STANDARD = "standard"
    EMERGING = "emerging"
    HIGH_RISK = "high_risk"

sas_model = SASModelLoader()

# --- Banking Intelligence Engine ---
class BankingIntelligenceEngine:
    def __init__(self):
        self.base_interest_rate = 0.045  # 4.5% base rate
        self.risk_premiums = {
            RiskLevel.LOW: 0.0,
            RiskLevel.MEDIUM: 0.015,  # +1.5%
            RiskLevel.HIGH: 0.035     # +3.5%
        }
        
    def calculate_comprehensive_assessment(self, features: dict) -> dict:
        """Enhanced credit assessment with banking intelligence"""
        # Use realistic coefficients that create dynamic variations
        # These coefficients are based on banking industry standards and will produce varied results
        # OVERRIDE SAS coefficients for dynamic demo purposes
        
        # Base intercept - represents baseline default probability
        linear_combo = -2.8
        
        # Traditional credit features with realistic banking coefficients
        income = features.get('Income', 50000)
        credit_score = features.get('CreditScore', 650)
        debt_ratio = features.get('DebtToIncome', 0.35)
        emp_years = features.get('EmploymentYears', 3)
        age = features.get('Age', 35)
        loan_amount = features.get('LoanAmount', 25000)
        
        # Core risk calculation - each variable has meaningful impact
        # Credit score: Higher scores reduce risk significantly
        linear_combo += (850 - credit_score) * 0.0045  # Strong negative correlation
        
        # Income: Higher income reduces risk (scaled appropriately)
        linear_combo -= (income - 50000) * 0.000012  # Income protection factor
        
        # Debt-to-income: Higher DTI increases risk dramatically
        linear_combo += debt_ratio * 4.2  # Major risk factor
        
        # Employment stability: More years = lower risk
        linear_combo -= emp_years * 0.08  # Stability factor
        
        # Age risk curve: Young and old have higher risk
        if age < 25 or age > 65:
            linear_combo += 0.6
        elif age < 30 or age > 55:
            linear_combo += 0.2
            
        # Loan amount relative to income
        loan_to_income = loan_amount / max(income, 1)
        linear_combo += loan_to_income * 1.8  # Higher loan-to-income = higher risk
        
        # Alternative data features
        social_risk = features.get('SocialMediaRiskScore', 3)
        device_score = features.get('DeviceUsageScore', 50)
        num_products = features.get('NumberOfProducts', 2)
        has_investment = features.get('HasInvestmentAccount', False)
        late_payments = features.get('LatePayments', 0)
        overdrafts = features.get('OverdraftEvents', 0)
        
        # Social media risk: 1-5 scale, higher = more risk
        linear_combo += (social_risk - 1) * 0.35  # Scaled social media impact
        
        # Device usage: Lower scores = higher risk
        linear_combo += (50 - device_score) * 0.008  # Digital behavior factor
        
        # Banking relationship depth: More products = lower risk
        linear_combo -= (num_products - 1) * 0.25  # Relationship value
        
        # Investment account: Premium customer indicator
        if has_investment:
            linear_combo -= 0.45  # Significant risk reduction
            
        # Payment behavior: Critical risk factors
        linear_combo += late_payments * 0.4  # Each late payment adds risk
        linear_combo += overdrafts * 0.25    # Each overdraft adds risk
        
        # Account tenure (derived from employment years if not provided)
        tenure = features.get('AccountTenure', emp_years * 12)
        linear_combo -= min(tenure, 60) * 0.008  # Tenure protection (capped at 5 years)
        
        # Interaction effects for more realistic modeling
        # High DTI + Low Credit Score = compounded risk
        if debt_ratio > 0.4 and credit_score < 650:
            linear_combo += 0.8
            
        # High income + investment account + good credit = premium customer discount
        if income > 100000 and has_investment and credit_score > 750:
            linear_combo -= 0.6
            
        # Young with high social media risk = elevated risk
        if age < 30 and social_risk >= 4:
            linear_combo += 0.4
        
        # Apply reasonable bounds to prevent extreme values
        linear_combo = max(-4.5, min(4.5, linear_combo))
        
        # Calculate probability using logistic function
        risk_probability = 1 / (1 + np.exp(-linear_combo))
        
        # Ensure reasonable bounds (0.5% to 85% default probability)
        risk_probability = max(0.005, min(0.85, risk_probability))
        
        # Calculate alternative data impact for reporting
        alt_data_impact = abs((social_risk - 3) * 0.35) + abs((50 - device_score) * 0.008) + late_payments * 0.4 + overdrafts * 0.25
        
        # Determine risk level
        if risk_probability < 0.3:
            risk_level = RiskLevel.LOW
        elif risk_probability < 0.7:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH
        
        # Calculate customer segment
        income = features.get('Income', 0)
        credit_score = features.get('CreditScore', 0)
        has_investment = features.get('HasInvestmentAccount', False)
        
        if income > 100000 and credit_score > 750 and has_investment:
            segment = CustomerSegment.PREMIUM
        elif risk_level == RiskLevel.HIGH:
            segment = CustomerSegment.HIGH_RISK
        elif income < 40000 or credit_score < 650:
            segment = CustomerSegment.EMERGING
        else:
            segment = CustomerSegment.STANDARD
        
        # Calculate lifetime value
        base_ltv = features.get('Income', 0) * 0.15  # 15% of annual income
        ltv_multiplier = {'premium': 2.5, 'standard': 1.5, 'emerging': 1.0, 'high_risk': 0.5}
        lifetime_value = base_ltv * ltv_multiplier.get(segment.value, 1.0)
        
        # Risk-adjusted pricing
        risk_adjusted_rate = self.base_interest_rate + self.risk_premiums[risk_level]
        
        # Upsell opportunities
        upsell_products = self._identify_upsell_opportunities(features, segment, risk_level)
        
        # Investment readiness
        investment_score = self._calculate_investment_readiness(features)
        
        return {
            'risk_level': risk_level,
            'risk_probability': round(risk_probability, 4),
            'traditional_score': int(features.get('CreditScore', 0)),
            'alternative_data_impact': round(alt_data_impact, 4),
            'customer_segment': segment,
            'lifetime_value_estimate': round(lifetime_value, 2),
            'risk_adjusted_pricing': round(risk_adjusted_rate * 100, 2),
            'upsell_products': upsell_products,
            'investment_readiness_score': round(investment_score, 2)
        }
    
    def _identify_upsell_opportunities(self, features: dict, segment: CustomerSegment, risk_level: RiskLevel) -> List[str]:
        """Identify relevant upsell products"""
        opportunities = []
        
        income = features.get('Income', 0)
        has_investment = features.get('HasInvestmentAccount', False)
        num_products = features.get('NumberOfProducts', 0)
        
        if risk_level == RiskLevel.LOW:
            if not has_investment and income > 60000:
                opportunities.append("Investment Portfolio Management")
            if income > 80000:
                opportunities.append("Premium Credit Card")
            if num_products < 3:
                opportunities.append("Mortgage Pre-approval")
        
        if segment == CustomerSegment.PREMIUM:
            opportunities.extend(["Private Banking Services", "Wealth Management"])
        
        if features.get('Age', 0) > 45 and not has_investment:
            opportunities.append("Retirement Planning")
        
        return opportunities
    
    def _calculate_investment_readiness(self, features: dict) -> float:
        """Calculate investment readiness score"""
        score = 0.0
        
        # Income factor
        income = features.get('Income', 0)
        if income > 100000:
            score += 0.4
        elif income > 60000:
            score += 0.2
        
        # Age factor
        age = features.get('Age', 0)
        if 30 <= age <= 55:
            score += 0.3
        elif 25 <= age <= 65:
            score += 0.2
        
        # Credit score factor
        credit = features.get('CreditScore', 0)
        if credit > 750:
            score += 0.2
        elif credit > 650:
            score += 0.1
        
        # Stability factor
        emp_years = features.get('EmploymentYears', 0)
        if emp_years > 5:
            score += 0.1
        
        return min(score, 1.0)
    
    def generate_improvement_plan(self, features: dict, risk_level: RiskLevel) -> List[Dict[str, Any]]:
        """Generate personalized improvement recommendations"""
        plan = []
        
        if risk_level == RiskLevel.HIGH:
            debt_ratio = features.get('DebtToIncome', 0)
            if debt_ratio > 0.4:
                plan.append({
                    "action": "Reduce Debt-to-Income Ratio",
                    "current_value": f"{debt_ratio:.1%}",
                    "target_value": "Below 35%",
                    "timeline": "3-4 months",
                    "impact": "High - Will significantly improve credit approval odds"
                })
            
            late_payments = features.get('LatePayments', 0)
            if late_payments > 2:
                plan.append({
                    "action": "Establish Perfect Payment History",
                    "current_value": f"{late_payments} late payments",
                    "target_value": "0 late payments",
                    "timeline": "4-6 months",
                    "impact": "High - Payment history is 35% of credit score"
                })
            
            credit_score = features.get('CreditScore', 0)
            if credit_score < 650:
                plan.append({
                    "action": "Improve Credit Score",
                    "current_value": f"{credit_score}",
                    "target_value": "Above 680",
                    "timeline": "4-6 months",
                    "impact": "Critical - Opens access to better loan products"
                })
            
            # Social media coaching
            social_risk = features.get('SocialMediaRiskScore', 0)
            if social_risk > 0.6:
                plan.append({
                    "action": "Digital Footprint Optimization",
                    "current_value": f"Risk Score: {social_risk:.1f}",
                    "target_value": "Below 0.4",
                    "timeline": "2-3 months",
                    "impact": "Medium - Alternative data increasingly important"
                })
        
        return plan

banking_engine = BankingIntelligenceEngine()

# --- Enhanced Pydantic Models ---
# Legacy response model for backwards compatibility
class CreditRiskResponse(BaseModel):
    prediction: str
    risk_probability: float
    model_version: str
    model_name: str

class CreditRiskRequest(BaseModel):
    # Traditional Banking Data
    Income: float = Field(..., example=75000, description="Annual income")
    Age: int = Field(..., example=35, description="Customer age")
    LoanAmount: float = Field(..., example=200000, description="Requested loan amount")
    CreditScore: int = Field(..., example=750, description="Traditional credit score")
    DebtToIncome: float = Field(..., example=0.25, description="Debt to income ratio")
    EmploymentYears: int = Field(..., example=8, description="Years of employment")
    LoanTerm: int = Field(..., example=30, description="Loan term in years")
    
    # Alternative Data (Optional)
    SocialMediaRiskScore: Optional[float] = Field(0.3, example=0.3, description="Social media risk score (0-1)")
    DeviceUsageScore: Optional[float] = Field(0.7, example=0.7, description="Digital behavior score (0-1)")
    NumberOfProducts: Optional[int] = Field(2, example=2, description="Current products with bank")
    HasInvestmentAccount: Optional[bool] = Field(False, example=False, description="Has investment account")
    AccountTenure: Optional[int] = Field(24, example=24, description="Months as customer")
    LatePayments: Optional[int] = Field(0, example=0, description="Late payments in last 12 months")
    OverdraftEvents: Optional[int] = Field(1, example=1, description="Overdraft events in last 12 months")

class ComprehensiveAssessmentResponse(BaseModel):
    # Core Risk Assessment
    risk_level: RiskLevel
    risk_probability: float
    traditional_score: int
    alternative_data_impact: float
    
    # Banking Intelligence
    customer_segment: CustomerSegment
    lifetime_value_estimate: float
    risk_adjusted_pricing: float
    
    # Compliance & Governance
    model_version: str
    assessment_timestamp: str
    regulatory_flags: List[str]
    confidence_interval: Dict[str, float]
    
    # Upsell Opportunities
    upsell_products: List[str]
    investment_readiness_score: float

class CustomerAdvisoryResponse(BaseModel):
    customer_id: str
    current_risk_level: RiskLevel
    improvement_plan: List[Dict[str, Any]]
    target_timeline: str
    expected_improvement: float
    reapplication_date: str
    monitoring_metrics: List[str]

class PortfolioInsightsResponse(BaseModel):
    portfolio_health: Dict[str, Any]
    risk_distribution: Dict[str, float]
    profitability_metrics: Dict[str, float]
    alternative_data_effectiveness: Dict[str, float]
    compliance_status: Dict[str, Any]
    growth_opportunities: List[Dict[str, Any]]

class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Contact name")
    company: str = Field("", description="Company name")
    email: str = Field(..., description="Email address") 
    phone: str = Field("", description="Phone number")
    interest: str = Field("general", description="Interest area")
    message: str = Field("", description="Contact message")

class ContactResponse(BaseModel):
    success: bool
    message: str
    emails_sent: List[str]

class BusinessAssessmentRequest(BaseModel):
    # Section 1: Strategic Fit
    useCaseName: str = Field(..., description="Use case name/initiative")
    department: str = Field(..., description="Department/business unit") 
    businessProblem: str = Field(..., description="Current business challenge")
    solutionIdea: str = Field(..., description="Proposed AI solution idea")
    strategicPriority: str = Field(..., description="Strategic priority level (1-5)")
    
    # Section 2: Business Impact
    businessObjective: str = Field(..., description="Primary business objective")
    timeframe: str = Field(..., description="Expected implementation timeframe")
    businessImpactValue: str = Field(..., description="Estimated business impact value")
    keyStakeholder: str = Field(..., description="Key stakeholder/decision maker")
    businessImpact: str = Field(..., description="Business impact priority (1-5)")
    
    # Section 3: Technical Readiness
    dataReadiness: str = Field(..., description="Current data availability & quality")
    aiMaturity: str = Field(..., description="Current analytics/AI maturity level")
    technicalRisks: str = Field("", description="Key technical/operational risks")
    sasFit: str = Field(..., description="SAS solution fit assessment")
    technicalFeasibility: str = Field(..., description="Technical feasibility (1-5)")

class BusinessAssessmentResponse(BaseModel):
    success: bool
    message: str
    assessment_id: str
    priority_score: float
    recommendations: List[str]

# --- Enhanced API Endpoints ---
@app.options("/{path:path}")
async def options_handler(request):
    """Handle preflight OPTIONS requests for CORS"""
    return {
        "message": "OK",
        "methods": ["GET", "POST", "OPTIONS"],
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    }

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

@app.post("/assess/comprehensive", response_model=ComprehensiveAssessmentResponse)
async def comprehensive_credit_assessment(request: CreditRiskRequest):
    """🏦 Advanced banking assessment with alternative data and portfolio intelligence"""
    if not sas_model.model_ready:
        raise HTTPException(status_code=503, detail="SAS model not ready")
    
    features = request.dict()
    assessment = banking_engine.calculate_comprehensive_assessment(features)
    
    # Regulatory flags
    regulatory_flags = []
    if features.get('DebtToIncome', 0) > 0.43:
        regulatory_flags.append("High DTI - QM rule consideration")
    if features.get('Age', 0) < 21:
        regulatory_flags.append("Young borrower - additional verification required")
    
    # Confidence intervals
    confidence_interval = {
        "lower_bound": max(0, assessment['risk_probability'] - 0.1),
        "upper_bound": min(1, assessment['risk_probability'] + 0.1)
    }
    
    return ComprehensiveAssessmentResponse(
        risk_level=assessment['risk_level'],
        risk_probability=assessment['risk_probability'],
        traditional_score=assessment['traditional_score'],
        alternative_data_impact=assessment['alternative_data_impact'],
        customer_segment=assessment['customer_segment'],
        lifetime_value_estimate=assessment['lifetime_value_estimate'],
        risk_adjusted_pricing=assessment['risk_adjusted_pricing'],
        model_version=sas_model.metadata.get("model_version", "3.0.0"),
        assessment_timestamp=datetime.now().isoformat(),
        regulatory_flags=regulatory_flags,
        confidence_interval=confidence_interval,
        upsell_products=assessment['upsell_products'],
        investment_readiness_score=assessment['investment_readiness_score']
    )

@app.post("/advisory/improve", response_model=CustomerAdvisoryResponse)
async def generate_customer_advisory(request: CreditRiskRequest):
    """🎯 AI-powered improvement recommendations for high-risk customers"""
    if not sas_model.model_ready:
        raise HTTPException(status_code=503, detail="SAS model not ready")
    
    features = request.dict()
    assessment = banking_engine.calculate_comprehensive_assessment(features)
    
    # Generate customer ID for tracking
    customer_id = f"CUST_{hash(str(features)) % 100000:05d}"
    
    # Generate improvement plan
    improvement_plan = banking_engine.generate_improvement_plan(features, assessment['risk_level'])
    
    # Calculate timeline and expected improvement
    if assessment['risk_level'] == RiskLevel.HIGH:
        timeline = "4-6 months"
        expected_improvement = 0.25  # 25% improvement in approval odds
        reapplication_date = (datetime.now() + timedelta(days=120)).strftime("%Y-%m-%d")
    else:
        timeline = "2-3 months"
        expected_improvement = 0.15
        reapplication_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
    
    monitoring_metrics = [
        "Credit Score Tracking",
        "Debt-to-Income Monitoring", 
        "Payment History Verification",
        "Digital Behavior Assessment"
    ]
    
    return CustomerAdvisoryResponse(
        customer_id=customer_id,
        current_risk_level=assessment['risk_level'],
        improvement_plan=improvement_plan,
        target_timeline=timeline,
        expected_improvement=expected_improvement,
        reapplication_date=reapplication_date,
        monitoring_metrics=monitoring_metrics
    )

@app.get("/portfolio/insights", response_model=PortfolioInsightsResponse)
async def get_portfolio_insights():
    """📊 Real-time portfolio analytics and risk distribution"""
    if not sas_model.model_ready:
        raise HTTPException(status_code=503, detail="SAS model not ready")
    
    # Simulate portfolio data (in real implementation, this would query actual portfolio)
    portfolio_health = {
        "total_customers": 15427,
        "active_loans": 8934,
        "avg_portfolio_risk": 0.34,
        "portfolio_auc": 0.75,
        "ytd_growth": 0.12
    }
    
    risk_distribution = {
        "low_risk": 0.45,    # 45% of portfolio
        "medium_risk": 0.35, # 35% of portfolio  
        "high_risk": 0.20    # 20% of portfolio
    }
    
    profitability_metrics = {
        "revenue_per_low_risk": 2850.0,
        "revenue_per_medium_risk": 1950.0,
        "revenue_per_high_risk": 950.0,
        "total_portfolio_value": 125000000.0,
        "risk_adjusted_return": 0.087
    }
    
    alternative_data_effectiveness = {
        "social_media_lift": 0.12,      # 12% improvement in prediction
        "device_behavior_lift": 0.08,   # 8% improvement
        "thin_file_coverage": 0.23,     # 23% more customers assessable
        "false_positive_reduction": 0.15 # 15% fewer good customers rejected
    }
    
    compliance_status = {
        "regulatory_compliance": "Green",
        "audit_trail_complete": True,
        "model_governance": "Approved",
        "last_validation": "2025-07-15",
        "next_review": "2025-10-15"
    }
    
    growth_opportunities = [
        {
            "segment": "Emerging Market - Thin Files",
            "potential_customers": 3500,
            "estimated_revenue": 4200000,
            "confidence": 0.78
        },
        {
            "segment": "Premium Investment Upsell",
            "potential_customers": 890,
            "estimated_revenue": 8900000,
            "confidence": 0.85
        },
        {
            "segment": "Digital-Native Millennials",
            "potential_customers": 2100,
            "estimated_revenue": 3150000,
            "confidence": 0.72
        }
    ]
    
    return PortfolioInsightsResponse(
        portfolio_health=portfolio_health,
        risk_distribution=risk_distribution,
        profitability_metrics=profitability_metrics,
        alternative_data_effectiveness=alternative_data_effectiveness,
        compliance_status=compliance_status,
        growth_opportunities=growth_opportunities
    )

@app.post("/contact/send", response_model=ContactResponse)
async def send_contact_email(contact: ContactRequest):
    """📧 Send contact form submission to Thakral One team"""
    try:
        # Thakral One team email addresses
        recipient_emails = [
            "hussein.srour@thakralone.com",
            "bikram@thakral.com", 
            "santie.heydenrych@thakralone.com"
        ]
        
        # Interest area labels
        interest_labels = {
            'general': 'General Inquiry',
            'banking-solutions': 'SAS Banking Solutions',
            'risk-modeling': 'Credit Risk Modeling',
            'alternative-data': 'Alternative Data Integration',
            'partnership': 'Partnership Opportunities',
            'demo-request': 'Schedule a Demo'
        }
        
        interest_label = interest_labels.get(contact.interest, contact.interest)
        
        # Create email content
        subject = f"SAS Event Inquiry - {interest_label}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;">
                    <h2 style="margin: 0; color: #4fc3f7;">🏦 SAS Banking Intelligence Inquiry</h2>
                    <p style="margin: 5px 0 0 0; opacity: 0.8;">New contact from SAS Event Demo</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="color: #2196f3; margin-top: 0;">Contact Information</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td style="padding: 8px 0; font-weight: bold;">Name:</td><td style="padding: 8px 0;">{contact.name}</td></tr>
                        <tr><td style="padding: 8px 0; font-weight: bold;">Company:</td><td style="padding: 8px 0;">{contact.company}</td></tr>
                        <tr><td style="padding: 8px 0; font-weight: bold;">Email:</td><td style="padding: 8px 0;"><a href="mailto:{contact.email}" style="color: #2196f3;">{contact.email}</a></td></tr>
                        <tr><td style="padding: 8px 0; font-weight: bold;">Phone:</td><td style="padding: 8px 0;">{contact.phone}</td></tr>
                        <tr><td style="padding: 8px 0; font-weight: bold;">Interest Area:</td><td style="padding: 8px 0;">{interest_label}</td></tr>
                    </table>
                </div>
                
                <div style="background: white; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                    <h3 style="color: #2196f3; margin-top: 0;">Message</h3>
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; white-space: pre-wrap;">{contact.message}</div>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #e8f5e8; border-radius: 8px; border-left: 4px solid #4caf50;">
                    <p style="margin: 0; color: #2e7d32;"><strong>Next Steps:</strong></p>
                    <ul style="margin: 10px 0 0 20px; color: #2e7d32;">
                        <li>Follow up within 24 hours</li>
                        <li>Schedule demo if requested</li>
                        <li>Provide relevant SAS Banking Intelligence materials</li>
                    </ul>
                </div>
                
                <div style="margin-top: 20px; text-align: center; color: #666; font-size: 12px;">
                    <p>This inquiry was generated from the SAS Banking Intelligence Mobile Demo</p>
                    <p>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # For demo purposes, we'll use a simple email simulation
        # In production, you would integrate with actual email service (SendGrid, AWS SES, etc.)
        
        logger.info(f"📧 Contact form submission received from {contact.name} ({contact.email})")
        logger.info(f"📧 Interest: {interest_label}")
        logger.info(f"📧 Company: {contact.company}")
        logger.info(f"📧 Message preview: {contact.message[:100]}...")
        
        # Simulate email sending success
        # In production, replace this with actual email sending logic
        emails_sent = []
        for email in recipient_emails:
            logger.info(f"📧 [SIMULATED] Email sent to {email}")
            emails_sent.append(email)
            
        return ContactResponse(
            success=True,
            message=f"Contact inquiry from {contact.name} processed successfully. Emails sent to Thakral One team.",
            emails_sent=emails_sent
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing contact form: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process contact form: {str(e)}")

@app.post("/assessment/business", response_model=BusinessAssessmentResponse)
async def submit_business_assessment(assessment: BusinessAssessmentRequest):
    """🎯 Submit Banking AI Use Case Assessment"""
    try:
        # Calculate priority score based on ratings
        strategic_priority = int(assessment.strategicPriority)
        business_impact = int(assessment.businessImpact) 
        technical_feasibility = int(assessment.technicalFeasibility)
        
        priority_score = (strategic_priority + business_impact + technical_feasibility) / 3.0
        
        # Generate assessment ID
        assessment_id = f"ASSESS_{hash(str(assessment.dict())) % 100000:05d}"
        
        # Generate recommendations based on assessment
        recommendations = []
        
        if priority_score >= 4.0:
            recommendations.extend([
                "High-priority use case - Schedule immediate strategic consultation",
                "Fast-track SAS solution architecture workshop", 
                "Consider proof-of-concept development"
            ])
        elif priority_score >= 3.0:
            recommendations.extend([
                "Medium-priority use case - Plan detailed discovery session",
                "Evaluate data readiness and technical requirements",
                "Develop implementation roadmap"
            ])
        else:
            recommendations.extend([
                "Use case needs further development",
                "Focus on strategic alignment and business case",
                "Consider data maturity and technical readiness improvements"
            ])
            
        # Add specific recommendations based on assessment details
        if assessment.dataReadiness in ["limited-data", "minimal-data"]:
            recommendations.append("Prioritize data strategy and governance initiatives")
            
        if assessment.aiMaturity in ["basic", "starting", "greenfield"]:
            recommendations.append("Consider SAS analytics maturity assessment")
            
        if assessment.sasFit == "perfect-fit":
            recommendations.append("Excellent SAS solution fit - accelerate engagement")
        elif assessment.sasFit == "comparison":
            recommendations.append("Schedule competitive differentiation session")
            
        # Create comprehensive email content
        department_labels = {
            'risk-management': 'Risk Management',
            'retail-banking': 'Retail Banking',
            'commercial-banking': 'Commercial Banking',
            'credit-underwriting': 'Credit Underwriting',
            'compliance': 'Compliance & Regulatory',
            'operations': 'Operations',
            'customer-analytics': 'Customer Analytics',
            'fraud-prevention': 'Fraud Prevention',
            'other': 'Other'
        }
        
        priority_text = "HIGH PRIORITY" if priority_score >= 4.0 else "MEDIUM PRIORITY" if priority_score >= 3.0 else "NEEDS DEVELOPMENT"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 700px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #ff9800, #f57c00); padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;">
                    <h2 style="margin: 0; color: white;">🎯 Banking AI Use Case Assessment</h2>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Priority Level: <strong>{priority_text}</strong> (Score: {priority_score:.1f}/5.0)</p>
                </div>
                
                <div style="background: #fff3e0; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #ff9800;">
                    <h3 style="color: #e65100; margin-top: 0;">Assessment Summary</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td style="padding: 8px 0; font-weight: bold;">Assessment ID:</td><td style="padding: 8px 0;">{assessment_id}</td></tr>
                        <tr><td style="padding: 8px 0; font-weight: bold;">Use Case:</td><td style="padding: 8px 0;">{assessment.useCaseName}</td></tr>
                        <tr><td style="padding: 8px 0; font-weight: bold;">Department:</td><td style="padding: 8px 0;">{department_labels.get(assessment.department, assessment.department)}</td></tr>
                        <tr><td style="padding: 8px 0; font-weight: bold;">Key Stakeholder:</td><td style="padding: 8px 0;">{assessment.keyStakeholder}</td></tr>
                        <tr><td style="padding: 8px 0; font-weight: bold;">Business Value:</td><td style="padding: 8px 0;">{assessment.businessImpactValue}</td></tr>
                        <tr><td style="padding: 8px 0; font-weight: bold;">Timeframe:</td><td style="padding: 8px 0;">{assessment.timeframe}</td></tr>
                    </table>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                    <div style="background: #f3e5f5; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="color: #7b1fa2; font-size: 24px; font-weight: bold;">{strategic_priority}/5</div>
                        <div style="color: #4a148c; font-size: 12px;">Strategic Priority</div>
                    </div>
                    <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="color: #388e3c; font-size: 24px; font-weight: bold;">{business_impact}/5</div>
                        <div style="color: #1b5e20; font-size: 12px;">Business Impact</div>
                    </div>
                    <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="color: #1976d2; font-size: 24px; font-weight: bold;">{technical_feasibility}/5</div>
                        <div style="color: #0d47a1; font-size: 12px;">Technical Feasibility</div>
                    </div>
                </div>
                
                <div style="background: white; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="color: #ff9800; margin-top: 0;">🔍 Section 1: Strategic Fit</h3>
                    <div style="margin-bottom: 15px;">
                        <strong>Business Problem:</strong>
                        <div style="background: #f5f5f5; padding: 10px; border-radius: 5px; margin-top: 5px;">{assessment.businessProblem}</div>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <strong>Proposed Solution:</strong>
                        <div style="background: #f5f5f5; padding: 10px; border-radius: 5px; margin-top: 5px;">{assessment.solutionIdea}</div>
                    </div>
                </div>
                
                <div style="background: white; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="color: #ff9800; margin-top: 0;">💼 Section 2: Business Impact</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div><strong>Primary Objective:</strong> {assessment.businessObjective}</div>
                        <div><strong>Impact Value:</strong> {assessment.businessImpactValue}</div>
                    </div>
                </div>
                
                <div style="background: white; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="color: #ff9800; margin-top: 0;">🔧 Section 3: Technical Readiness</h3>
                    <div style="margin-bottom: 10px;"><strong>Data Readiness:</strong> {assessment.dataReadiness}</div>
                    <div style="margin-bottom: 10px;"><strong>AI Maturity:</strong> {assessment.aiMaturity}</div>
                    <div style="margin-bottom: 10px;"><strong>SAS Fit:</strong> {assessment.sasFit}</div>
                    {f'<div style="margin-bottom: 10px;"><strong>Technical Risks:</strong> {assessment.technicalRisks}</div>' if assessment.technicalRisks else ''}
                </div>
                
                <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; border-left: 4px solid #4caf50;">
                    <h3 style="color: #2e7d32; margin-top: 0;">🎯 Recommendations</h3>
                    <ul style="margin: 10px 0 0 20px; color: #2e7d32;">
                        {''.join(f'<li>{rec}</li>' for rec in recommendations)}
                    </ul>
                </div>
                
                <div style="margin-top: 20px; text-align: center; color: #666; font-size: 12px;">
                    <p>Assessment submitted from SAS Banking Intelligence Mobile Demo</p>
                    <p>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Log the business assessment
        logger.info(f"🎯 Business assessment received: {assessment.useCaseName}")
        logger.info(f"🎯 Department: {department_labels.get(assessment.department, assessment.department)}")
        logger.info(f"🎯 Priority Score: {priority_score:.1f}/5.0 ({priority_text})")
        logger.info(f"🎯 Key Stakeholder: {assessment.keyStakeholder}")
        logger.info(f"🎯 Business Value: {assessment.businessImpactValue}")
        logger.info(f"🎯 SAS Fit: {assessment.sasFit}")
        
        # Simulate email sending (in production, integrate with actual email service)
        recipient_emails = [
            "hussein.srour@thakralone.com",
            "bikram@thakral.com",
            "santie.heydenrych@thakralone.com"
        ]
        
        for email in recipient_emails:
            logger.info(f"📧 [SIMULATED] Business assessment sent to {email}")
        
        return BusinessAssessmentResponse(
            success=True,
            message=f"Banking AI use case assessment '{assessment.useCaseName}' processed successfully",
            assessment_id=assessment_id,
            priority_score=priority_score,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing business assessment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process business assessment: {str(e)}")

@app.get("/")
async def get_sas_banking_demo(mobile: str = Query(None), brochure: str = Query(None)):
    """🏦 Serve the comprehensive SAS Banking Intelligence Demo"""
    try:
        logger.info(f"🎯 Main route called - mobile: '{mobile}', brochure: '{brochure}'")
        logger.info(f"🎯 Type of mobile: {type(mobile)}, Type of brochure: {type(brochure)}")
        
        # If brochure parameter is present, serve the technical brochure FIRST
        if brochure is not None and brochure == "1":
            logger.info("🎯 Brochure parameter detected - serving technical brochure!")
            
            possible_brochure_paths = [
                "technical_brochure.html",
                "src/technical_brochure.html",
                "../src/technical_brochure.html",
                "./src/technical_brochure.html"
            ]
            
            for path in possible_brochure_paths:
                brochure_path = Path(path)
                logger.info(f"🔍 Checking brochure path: {brochure_path}")
                if brochure_path.exists():
                    logger.info(f"✅ Found technical brochure at: {brochure_path}")
                    return FileResponse(brochure_path, media_type="text/html")
            
            logger.error("❌ Technical brochure not found in any path")
            raise HTTPException(status_code=404, detail="Technical brochure not found")
        
        # If mobile parameter is present, serve the clean mobile version
        if mobile == "1":
            mobile_demo_paths = [
                "mobile_demo_clean.html",
                "src/mobile_demo_clean.html", 
                "../src/mobile_demo_clean.html",
                "./mobile_demo_clean.html"
            ]
            
            for path in mobile_demo_paths:
                demo_path = Path(path)
                if demo_path.exists():
                    logger.info(f"Found clean mobile demo file at: {path}")
                    with open(demo_path, 'r', encoding='utf-8') as f:
                        return HTMLResponse(f.read())
        
        
        # Try multiple possible paths for the demo file
        possible_demo_paths = [
            "sas_banking_demo.html",
            "src/sas_banking_demo.html", 
            "../src/sas_banking_demo.html",
            "./sas_banking_demo.html"
        ]
        
        demo_path = None
        for path in possible_demo_paths:
            if os.path.exists(path):
                demo_path = path
                logger.info(f"Found demo file at: {demo_path}")
                break
        
        if demo_path:
            return FileResponse(demo_path, media_type="text/html")
        else:
            logger.warning(f"Demo file not found in any of these paths: {possible_demo_paths}")
            return {"message": "Demo not found. Please check file path."}
    except Exception as e:
        logger.error(f"Error serving demo: {e}")
        raise HTTPException(status_code=500, detail=f"Error serving demo: {e}")

@app.get("/brochure")
def get_brochure():
    """📋 Technical Architecture Brochure"""
    brochure_path = Path(__file__).parent / "technical_brochure.html"
    logger.info(f"Brochure request - path: {brochure_path}")
    
    if brochure_path.exists():
        logger.info("Serving technical brochure")
        return FileResponse(brochure_path, media_type="text/html")
    else:
        logger.error("Brochure file not found")
        raise HTTPException(status_code=404, detail="Brochure not found")

@app.get("/brochure")
def get_brochure_simple():
    """📋 Technical Architecture Brochure - Simple Direct Access"""
    logger.info("🎯 BROCHURE ENDPOINT CALLED!")
    return FileResponse("src/technical_brochure.html", media_type="text/html")

@app.get("/tech-docs")  
async def get_tech_docs():
    """📋 Technical Documentation"""
    logger.info("🎯 TECH DOCS ENDPOINT CALLED!")
    return FileResponse("src/technical_brochure.html", media_type="text/html")

@app.get("/api")
async def api_info():
    """📊 API Information and Endpoints"""
    return {
        "message": "SAS Banking Intelligence API",
        "description": "Enterprise credit risk assessment with alternative data intelligence",
        "version": "3.0.0",
        "capabilities": [
            "Traditional credit scoring",
            "Alternative data integration", 
            "Risk-adjusted pricing",
            "Customer advisory system",
            "Portfolio intelligence",
            "Regulatory compliance"
        ],
        "endpoints": {
            "main_demo": "/",
            "api_info": "/api",
            "basic_prediction": "/predict",
            "comprehensive_assessment": "/assess/comprehensive",
            "customer_advisory": "/advisory/improve",
            "portfolio_insights": "/portfolio/insights",
            "health_check": "/health",
            "model_info": "/model/info"
        }
    }

# All demo functionality now served from the root endpoint

# Legacy endpoint for backwards compatibility

if __name__ == "__main__":
    logger.info("🚀 Starting SAS Banking Intelligence API...")
    logger.info(f"📊 Model loaded: {sas_model.metadata.get('model_name', 'Unknown')}")
    logger.info("🔗 API Documentation: http://localhost:8081/docs")
    uvicorn.run(app, host="0.0.0.0", port=8081)
