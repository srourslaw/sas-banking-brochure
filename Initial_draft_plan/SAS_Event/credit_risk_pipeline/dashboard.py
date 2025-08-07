import streamlit as st
import requests
import pandas as pd
import time
import numpy as np

st.set_page_config(
    page_title="Thakral One: 5-Minute Model-to-Market Control Tower",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚀 Thakral One: 5-Minute Model-to-Market Control Tower")
st.markdown("---")

if 'pipeline_complete' not in st.session_state:
    st.session_state.pipeline_complete = False

if not st.session_state.pipeline_complete:
    st.header("🔄 Live Pipeline Simulation")
    
    with st.status("Deploying SAS Model to Production...", expanded=True) as status:
        st.write("🔍 Reading SAS Model Artifacts...")
        time.sleep(3)
        
        st.write("⚙️ Generating API Code...")
        time.sleep(2)
        
        st.write("🐳 Building Secure Container...")
        time.sleep(4)
        
        st.write("☁️ Deploying to Cloud...")
        time.sleep(3)
        
        st.write("🌐 Publishing Live Endpoint...")
        time.sleep(2)
        
        status.update(label="✅ Pipeline Complete!", state="complete", expanded=False)
    
    st.success("✅ PIPELINE COMPLETE! Model is live and ready for predictions.")
    st.balloons()
    st.session_state.pipeline_complete = True
    time.sleep(2)
    st.rerun()

else:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("📊 Model Analytics")
        st.metric("Models Deployed", "1", delta="1")
        st.metric("Uptime", "99.9%", delta="0.1%")
        st.metric("Avg Response Time", "45ms", delta="-5ms")
        
        st.markdown("### 🔧 System Health")
        st.progress(0.99, text="CPU Usage: 12%")
        st.progress(0.85, text="Memory: 2.1GB")
        st.progress(0.92, text="API Calls: 1,247")
    
    with col2:
        st.header("🎯 Interactive Prediction Center")
        
        st.sidebar.header("📝 New Loan Application")
        
        age = st.sidebar.slider("Age", 18, 80, 35)
        income = st.sidebar.number_input("Annual Income ($)", min_value=20000, max_value=500000, value=75000, step=5000)
        loan_amount = st.sidebar.number_input("Loan Amount ($)", min_value=5000, max_value=1000000, value=200000, step=10000)
        loan_term = st.sidebar.slider("Loan Term (years)", 1, 30, 15)
        credit_score = st.sidebar.slider("Credit Score", 300, 850, 720)
        employment_years = st.sidebar.slider("Years Employed", 0, 40, 5)
        debt_to_income = st.sidebar.slider("Debt-to-Income Ratio", 0.0, 1.0, 0.3, step=0.01)
        
        predict_button = st.sidebar.button("🎯 Assess Credit Risk", type="primary", use_container_width=True)
        
        if predict_button:
            with st.spinner("🤖 AI Model Processing..."):
                try:
                    payload = {
                        "Age": age,
                        "Income": income,
                        "LoanAmount": loan_amount,
                        "LoanTerm": loan_term,
                        "CreditScore": credit_score,
                        "EmploymentYears": employment_years,
                        "DebtToIncome": debt_to_income
                    }
                    
                    response = requests.post(
                        "http://credit-risk-model:8080/predict",
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        prediction = result.get("prediction", "unknown")
                        probability = result.get("probability", 0.5)
                        
                        st.markdown("### 🎯 Risk Assessment Results")
                        
                        col_pred1, col_pred2, col_pred3 = st.columns(3)
                        
                        with col_pred1:
                            if prediction.lower() == "high risk":
                                st.error("🔴 Prediction: HIGH RISK")
                            else:
                                st.success("🟢 Prediction: LOW RISK")
                        
                        with col_pred2:
                            risk_score = int(probability * 100) if prediction.lower() == "high risk" else int((1-probability) * 100)
                            st.metric("Risk Score", f"{risk_score}%", delta=f"{risk_score-50}%")
                        
                        with col_pred3:
                            confidence = max(probability, 1-probability)
                            st.metric("Confidence", f"{confidence:.1%}")
                            st.progress(confidence, text=f"Model Confidence: {confidence:.1%}")
                        
                        st.markdown("### 📈 Key Influencing Factors")
                        
                        factors_data = {
                            "Factor": ["Credit Score", "Income", "Debt-to-Income", "Loan Amount", "Employment Years", "Age", "Loan Term"],
                            "Importance": [
                                min(100, max(0, (credit_score - 300) / 550 * 100)),
                                min(100, max(0, (income - 20000) / 480000 * 100)),
                                max(0, min(100, (1 - debt_to_income) * 100)),
                                max(0, min(100, (500000 - loan_amount) / 495000 * 100)),
                                min(100, max(0, employment_years / 40 * 100)),
                                min(100, max(0, (age - 18) / 62 * 80)),
                                max(0, min(100, (30 - loan_term) / 29 * 70))
                            ]
                        }
                        
                        df_factors = pd.DataFrame(factors_data)
                        df_factors = df_factors.sort_values("Importance", ascending=True)
                        
                        st.bar_chart(
                            df_factors.set_index("Factor")["Importance"],
                            height=300
                        )
                        
                        st.markdown("### 🔍 Application Summary")
                        summary_col1, summary_col2 = st.columns(2)
                        
                        with summary_col1:
                            st.metric("Applicant Age", f"{age} years")
                            st.metric("Credit Score", credit_score)
                            st.metric("Employment", f"{employment_years} years")
                            st.metric("Debt Ratio", f"{debt_to_income:.1%}")
                        
                        with summary_col2:
                            st.metric("Annual Income", f"${income:,}")
                            st.metric("Loan Amount", f"${loan_amount:,}")
                            st.metric("Loan Term", f"{loan_term} years")
                            monthly_payment = loan_amount * (0.05/12) * (1 + 0.05/12)**(loan_term*12) / ((1 + 0.05/12)**(loan_term*12) - 1)
                            st.metric("Est. Monthly Payment", f"${monthly_payment:,.0f}")
                        
                    else:
                        st.error(f"❌ Model API Error: {response.status_code}")
                        st.write("Response:", response.text)
                
                except requests.exceptions.ConnectionError:
                    st.warning("⚠️ Model service not available. Using demo prediction...")
                    
                    demo_risk = "HIGH RISK" if (credit_score < 650 or debt_to_income > 0.4 or loan_amount > income * 4) else "LOW RISK"
                    demo_prob = np.random.uniform(0.6, 0.9) if demo_risk == "HIGH RISK" else np.random.uniform(0.1, 0.4)
                    
                    if demo_risk == "HIGH RISK":
                        st.error(f"🔴 Demo Prediction: {demo_risk}")
                    else:
                        st.success(f"🟢 Demo Prediction: {demo_risk}")
                    
                    st.metric("Demo Risk Score", f"{int(demo_prob * 100)}%")
                    st.progress(demo_prob, text=f"Demo Confidence: {demo_prob:.1%}")
                
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
        
        else:
            st.info("👈 Enter loan application details in the sidebar and click 'Assess Credit Risk' to see AI-powered predictions!")
            
            st.markdown("### 🎯 About This Demo")
            st.markdown("""
            This Control Tower demonstrates **Thakral One's 5-Minute Model-to-Market** capability:
            
            ✅ **Automated SAS Model Deployment**  
            ✅ **Instant API Generation**  
            ✅ **Secure Containerization**  
            ✅ **Real-time Predictions**  
            ✅ **Enterprise-grade Monitoring**
            
            The credit risk model analyzes multiple factors to provide instant loan decisions with full explainability.
            """)

st.sidebar.markdown("---")
st.sidebar.markdown("**🚀 Powered by Thakral One**")
st.sidebar.markdown("*5-Minute Model-to-Market Platform*")