#!/usr/bin/env python3
"""
🏦 SAS Banking Intelligence Demo Runner
Run this script to demonstrate the enhanced banking features
"""

import requests
import json
import time
import webbrowser
from datetime import datetime

API_BASE = "http://localhost:8080"

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is healthy - Model: {data.get('model_source', 'Unknown')}")
            return True
        else:
            print(f"❌ API health check failed - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("💡 Please run: docker-compose up --build")
        return False

def run_comprehensive_assessment(scenario="standard"):
    """Run comprehensive banking assessment"""
    scenarios = {
        "premium": {
            "Income": 150000, "Age": 42, "LoanAmount": 500000, "CreditScore": 780,
            "DebtToIncome": 0.15, "EmploymentYears": 15, "LoanTerm": 30,
            "SocialMediaRiskScore": 0.1, "DeviceUsageScore": 0.9, 
            "NumberOfProducts": 5, "HasInvestmentAccount": True,
            "AccountTenure": 60, "LatePayments": 0, "OverdraftEvents": 0
        },
        "standard": {
            "Income": 75000, "Age": 35, "LoanAmount": 200000, "CreditScore": 750,
            "DebtToIncome": 0.25, "EmploymentYears": 8, "LoanTerm": 30,
            "SocialMediaRiskScore": 0.3, "DeviceUsageScore": 0.7,
            "NumberOfProducts": 2, "HasInvestmentAccount": False,
            "AccountTenure": 24, "LatePayments": 0, "OverdraftEvents": 1
        },
        "highrisk": {
            "Income": 35000, "Age": 24, "LoanAmount": 250000, "CreditScore": 580,
            "DebtToIncome": 0.65, "EmploymentYears": 2, "LoanTerm": 30,
            "SocialMediaRiskScore": 0.8, "DeviceUsageScore": 0.3,
            "NumberOfProducts": 1, "HasInvestmentAccount": False,
            "AccountTenure": 8, "LatePayments": 4, "OverdraftEvents": 6
        }
    }
    
    if scenario not in scenarios:
        print(f"❌ Unknown scenario: {scenario}")
        return None
    
    print(f"\n🔍 Running {scenario.upper()} customer assessment...")
    
    try:
        response = requests.post(
            f"{API_BASE}/assess/comprehensive",
            json=scenarios[scenario],
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Assessment complete!")
            print(f"   Risk Level: {data['risk_level'].upper()}")
            print(f"   Risk Probability: {data['risk_probability']:.1%}")
            print(f"   Customer Segment: {data['customer_segment'].upper()}")
            print(f"   Lifetime Value: ${data['lifetime_value_estimate']:,.0f}")
            print(f"   Risk-Adjusted Rate: {data['risk_adjusted_pricing']:.2f}%")
            print(f"   Upsell Products: {', '.join(data['upsell_products'])}")
            return data
        else:
            print(f"❌ Assessment failed - Status: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def generate_customer_advisory():
    """Generate AI-powered customer advisory"""
    print(f"\n🎯 Generating customer advisory plan...")
    
    high_risk_customer = {
        "Income": 35000, "Age": 24, "LoanAmount": 250000, "CreditScore": 580,
        "DebtToIncome": 0.65, "EmploymentYears": 2, "LoanTerm": 30,
        "SocialMediaRiskScore": 0.8, "DeviceUsageScore": 0.3,
        "NumberOfProducts": 1, "HasInvestmentAccount": False,
        "AccountTenure": 8, "LatePayments": 4, "OverdraftEvents": 6
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/advisory/improve",
            json=high_risk_customer,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Advisory plan generated for Customer {data['customer_id']}")
            print(f"   Current Risk: {data['current_risk_level'].upper()}")
            print(f"   Timeline: {data['target_timeline']}")
            print(f"   Expected Improvement: {data['expected_improvement']:.0%}")
            print(f"   Reapplication Date: {data['reapplication_date']}")
            print(f"   Action Items: {len(data['improvement_plan'])} recommendations")
            return data
        else:
            print(f"❌ Advisory generation failed - Status: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def get_portfolio_insights():
    """Get portfolio analytics"""
    print(f"\n📈 Loading portfolio insights...")
    
    try:
        response = requests.get(f"{API_BASE}/portfolio/insights", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Portfolio data loaded!")
            print(f"   Total Customers: {data['portfolio_health']['total_customers']:,}")
            print(f"   Portfolio Value: ${data['profitability_metrics']['total_portfolio_value']:,.0f}")
            print(f"   Risk Distribution: {data['risk_distribution']['low_risk']:.0%} Low, {data['risk_distribution']['medium_risk']:.0%} Med, {data['risk_distribution']['high_risk']:.0%} High")
            print(f"   Social Media Lift: +{data['alternative_data_effectiveness']['social_media_lift']:.0%}")
            print(f"   Growth Opportunities: {len(data['growth_opportunities'])} identified")
            return data
        else:
            print(f"❌ Portfolio insights failed - Status: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def open_dashboard():
    """Open the interactive dashboard"""
    print(f"\n🎨 Opening Banking Intelligence Dashboard...")
    dashboard_url = f"{API_BASE}/dashboard"
    
    try:
        # Test if dashboard is accessible
        response = requests.get(dashboard_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Dashboard accessible at: {dashboard_url}")
            webbrowser.open(dashboard_url)
            return True
        else:
            print(f"❌ Dashboard not accessible - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot access dashboard: {e}")
        return False

def run_40_second_demo():
    """Simulate the 40-second deployment demo"""
    print(f"\n🎬 Starting 40-Second Model-to-Market Demo...")
    print(f"{'='*60}")
    
    stages = [
        (5, "🔄 SAS Model Studio - Model training complete"),
        (10, "📦 Model Artifacts - Exporting to JSON format"),
        (15, "🚀 GitHub Actions - Pipeline triggered automatically"),
        (20, "🐳 Docker Build - Creating production container"),
        (25, "🧪 Automated Testing - Running validation suite"),
        (30, "☁️ Cloud Deployment - Deploying to production"),
        (35, "✅ Health Checks - Verifying API endpoints"),
        (40, "🎉 LIVE! API ready for traffic")
    ]
    
    start_time = time.time()
    
    for target_time, message in stages:
        while time.time() - start_time < target_time:
            current = int(time.time() - start_time)
            print(f"\r⏱️  {40-current:02d} seconds remaining... ", end='', flush=True)
            time.sleep(0.5)
        
        print(f"\n{message}")
    
    print(f"\n{'='*60}")
    print(f"🏆 DEMO COMPLETE! SAS Model deployed in 40 seconds")
    print(f"📊 Traditional deployment: 4-6 weeks → 40 seconds = 99.9% time reduction")
    
    # Test the live API
    print(f"\n🔬 Testing live API...")
    health_data = check_api_health()
    if health_data:
        print(f"✅ API confirmed live and serving predictions!")

def main():
    """Main demo runner"""
    print(f"""
🏦 SAS Banking Intelligence Demo Runner
=====================================
Demonstrates the enhanced 40-second model-to-market pipeline
with sophisticated banking intelligence features.

Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
    
    # Check API health first
    if not check_api_health():
        return
    
    while True:
        print(f"""
📋 Demo Options:
1. 🔍 Comprehensive Credit Assessment (Premium Customer)
2. 🔍 Comprehensive Credit Assessment (Standard Customer)  
3. 🔍 Comprehensive Credit Assessment (High-Risk Customer)
4. 🎯 AI-Powered Customer Advisory
5. 📈 Portfolio Intelligence Analytics
6. 🎨 Open Interactive Dashboard
7. 🎬 Run 40-Second Live Demo
8. 🚪 Exit

Choose an option (1-8): """)
        
        choice = input().strip()
        
        if choice == '1':
            run_comprehensive_assessment("premium")
        elif choice == '2':
            run_comprehensive_assessment("standard")
        elif choice == '3':
            run_comprehensive_assessment("highrisk")
        elif choice == '4':
            generate_customer_advisory()
        elif choice == '5':
            get_portfolio_insights()
        elif choice == '6':
            open_dashboard()
        elif choice == '7':
            run_40_second_demo()
        elif choice == '8':
            print(f"\n👋 Demo session ended. Thank you!")
            break
        else:
            print(f"❌ Invalid option. Please choose 1-8.")

if __name__ == "__main__":
    main()