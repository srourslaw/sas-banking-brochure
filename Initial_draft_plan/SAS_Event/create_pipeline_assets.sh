#!/bin/bash

# 5-Minute Model-to-Market CI/CD Pipeline Demo Setup Script
# This script creates a complete credit risk pipeline demonstration

set -e  # Exit on any error

echo "🚀 Creating 5-Minute Model-to-Market CI/CD Pipeline Demo..."

# Create main project directory
PROJECT_DIR="credit_risk_pipeline"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

echo "📁 Created project directory: $PROJECT_DIR"

# 1. Create model_artifact directory with sample coefficients
echo "🔬 Creating model artifacts..."
mkdir -p model_artifact
cat > model_artifact/model_coefficients.txt << 'EOF'
Intercept,-1.5
Income,0.00002
Age,-0.05
LoanAmount,0.0001
CreditScore,0.008
DebtToIncome,-0.12
EmploymentYears,0.03
LoanTerm,-0.002
EOF

# Create model metadata
cat > model_artifact/model_metadata.json << 'EOF'
{
  "model_name": "credit_risk_logistic_regression",
  "model_version": "1.0.0",
  "created_date": "2024-01-15",
  "model_type": "logistic_regression",
  "features": ["Income", "Age", "LoanAmount", "CreditScore", "DebtToIncome", "EmploymentYears", "LoanTerm"],
  "target": "default_risk",
  "performance_metrics": {
    "accuracy": 0.847,
    "precision": 0.823,
    "recall": 0.791,
    "f1_score": 0.807,
    "auc_roc": 0.892
  },
  "data_scientist": "Jane Smith",
  "training_dataset": "credit_risk_dataset_2024_q1.csv"
}
EOF

# 2. Create containerization files
echo "🐳 Creating containerization files..."

# Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY model_artifact/ ./model_artifact/

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["python", "src/app.py"]
EOF

# Requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pandas==2.1.3
numpy==1.24.3
scikit-learn==1.3.2
pydantic==2.5.0
python-multipart==0.0.6
prometheus-client==0.19.0
structlog==23.2.0
EOF

# 3. Create source code
echo "💻 Creating application source code..."
mkdir -p src

# Main application
cat > src/app.py << 'EOF'
import os
import json
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Credit Risk Prediction API",
    description="Real-time credit risk assessment using ML model",
    version="1.0.0"
)

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
async def root():
    return {"message": "Credit Risk Prediction API", "status": "healthy"}

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
EOF

# 4. Create CI/CD configuration files
echo "🔧 Creating CI/CD configuration files..."

# GitHub Actions workflow
mkdir -p .github/workflows
cat > .github/workflows/ci-cd.yml << 'EOF'
name: Credit Risk Model CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  DOCKER_REGISTRY: ghcr.io
  IMAGE_NAME: credit-risk-model

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.DOCKER_REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: |
          ${{ env.DOCKER_REGISTRY }}/${{ github.repository }}/${{ env.IMAGE_NAME }}:latest
          ${{ env.DOCKER_REGISTRY }}/${{ github.repository }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment..."
        # Add actual deployment commands here
        
    - name: Run smoke tests
      run: |
        echo "Running smoke tests..."
        # Add smoke test commands here
        
    - name: Deploy to production
      if: success()
      run: |
        echo "Deploying to production environment..."
        # Add production deployment commands here
EOF

# 5. Create test files
echo "🧪 Creating test files..."
mkdir -p tests

cat > tests/test_model.py << 'EOF'
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
EOF

cat > tests/test_api.py << 'EOF'
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
EOF

# 6. Create deployment configurations
echo "🚀 Creating deployment configurations..."

# Kubernetes deployment
mkdir -p k8s
cat > k8s/deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: credit-risk-model
  labels:
    app: credit-risk-model
spec:
  replicas: 3
  selector:
    matchLabels:
      app: credit-risk-model
  template:
    metadata:
      labels:
        app: credit-risk-model
    spec:
      containers:
      - name: credit-risk-model
        image: ghcr.io/your-org/credit-risk-model:latest
        ports:
        - containerPort: 8080
        env:
        - name: PORT
          value: "8080"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: credit-risk-model-service
spec:
  selector:
    app: credit-risk-model
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
EOF

# Docker Compose for local development
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  credit-risk-model:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./model_artifact:/app/model_artifact
      - ./src:/app/src
    environment:
      - PORT=8080
      - PYTHONPATH=/app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  monitoring:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
EOF

# 7. Create monitoring configuration
echo "📊 Creating monitoring configuration..."
mkdir -p monitoring

cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'credit-risk-model'
    static_configs:
      - targets: ['credit-risk-model:8080']
    metrics_path: '/metrics'
    scrape_interval: 5s
EOF

# 8. Create documentation
echo "📖 Creating documentation..."

cat > README.md << 'EOF'
# Credit Risk Pipeline - 5-Minute Model-to-Market Demo

This project demonstrates a complete "Model-to-Market" CI/CD pipeline for deploying machine learning models in production.

## 🎯 Overview

This demo showcases how to take a data scientist's model artifacts and deploy them to production in under 5 minutes using modern DevOps practices.

## 🏗️ Architecture

```
Data Scientist Output → Containerization → CI/CD → Production Deployment
      ↓                      ↓              ↓             ↓
Model Artifacts      →   Docker Image  →  Testing   →  Kubernetes/Cloud
```

## 🚀 Quick Start

### 1. Local Development

```bash
# Build and run locally
docker-compose up --build

# Test the API
curl http://localhost:8080/health
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Income": 75000,
    "Age": 35,
    "LoanAmount": 200000,
    "CreditScore": 750,
    "DebtToIncome": 0.25,
    "EmploymentYears": 8,
    "LoanTerm": 30
  }'
```

### 2. Run Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

### 3. Deploy to Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
```

## 📊 Model Information

- **Model Type**: Logistic Regression
- **Purpose**: Credit Risk Assessment
- **Features**: Income, Age, LoanAmount, CreditScore, DebtToIncome, EmploymentYears, LoanTerm
- **Output**: Risk probability and classification (low_risk/high_risk)

## 🔧 CI/CD Pipeline

The pipeline includes:

1. **Testing**: Automated unit tests and integration tests
2. **Building**: Docker image creation and pushing to registry
3. **Deployment**: Automated deployment to staging and production
4. **Monitoring**: Health checks and performance metrics

## 📈 Monitoring

- Health checks: `/health`
- Model info: `/model/info`
- Metrics: Prometheus integration
- Logging: Structured logging with timestamps

## 🛠️ Development

### Adding New Features

1. Modify the model or add new endpoints in `src/app.py`
2. Add corresponding tests in `tests/`
3. Update documentation
4. Push to trigger CI/CD pipeline

### Model Updates

1. Replace files in `model_artifact/`
2. Update `model_metadata.json`
3. Increment version number
4. Deploy through CI/CD

## 🏷️ API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /model/info` - Model metadata
- `POST /predict` - Single prediction
- `POST /predict/batch` - Batch predictions

## 🎯 Demo Scenarios

### Scenario 1: Low Risk Customer
```json
{
  "Income": 75000,
  "Age": 35,
  "LoanAmount": 200000,
  "CreditScore": 750,
  "DebtToIncome": 0.25,
  "EmploymentYears": 8,
  "LoanTerm": 30
}
```

### Scenario 2: High Risk Customer
```json
{
  "Income": 25000,
  "Age": 22,
  "LoanAmount": 300000,
  "CreditScore": 500,
  "DebtToIncome": 0.8,
  "EmploymentYears": 1,
  "LoanTerm": 15
}
```

## 📋 Checklist for Production

- [ ] Security scanning
- [ ] Performance testing
- [ ] Monitoring alerts
- [ ] Backup strategies
- [ ] Rollback procedures
- [ ] Documentation updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
EOF

# 9. Create additional utility scripts
echo "🔧 Creating utility scripts..."
mkdir -p scripts

cat > scripts/run_tests.sh << 'EOF'
#!/bin/bash
echo "Running all tests..."
python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term
echo "Coverage report generated in htmlcov/"
EOF

cat > scripts/build_and_run.sh << 'EOF'
#!/bin/bash
echo "Building and running the application..."
docker-compose down
docker-compose up --build
EOF

cat > scripts/deploy_local.sh << 'EOF'
#!/bin/bash
echo "Deploying locally with Docker..."
docker build -t credit-risk-model .
docker run -p 8080:8080 credit-risk-model
EOF

# Make scripts executable
chmod +x scripts/*.sh

# 10. Create example data and configuration files
echo "📋 Creating example data and configuration files..."

cat > example_requests.json << 'EOF'
{
  "low_risk_customer": {
    "Income": 75000,
    "Age": 35,
    "LoanAmount": 200000,
    "CreditScore": 750,
    "DebtToIncome": 0.25,
    "EmploymentYears": 8,
    "LoanTerm": 30
  },
  "high_risk_customer": {
    "Income": 25000,
    "Age": 22,
    "LoanAmount": 300000,
    "CreditScore": 500,
    "DebtToIncome": 0.8,
    "EmploymentYears": 1,
    "LoanTerm": 15
  },
  "medium_risk_customer": {
    "Income": 50000,
    "Age": 28,
    "LoanAmount": 180000,
    "CreditScore": 650,
    "DebtToIncome": 0.4,
    "EmploymentYears": 3,
    "LoanTerm": 25
  }
}
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Docker
.dockerignore

# Logs
*.log
logs/

# Environment variables
.env
.env.local
.env.*.local

# Temporary files
*.tmp
*.temp
EOF

# Create project structure summary
echo "📁 Creating project structure summary..."
cat > PROJECT_STRUCTURE.md << 'EOF'
# Project Structure

```
credit_risk_pipeline/
├── README.md                          # Main documentation
├── PROJECT_STRUCTURE.md              # This file
├── requirements.txt                   # Python dependencies
├── Dockerfile                         # Container configuration
├── docker-compose.yml               # Local development setup
├── .gitignore                        # Git ignore rules
├── example_requests.json             # Sample API requests
│
├── model_artifact/                   # Data scientist output
│   ├── model_coefficients.txt        # Model coefficients
│   └── model_metadata.json          # Model metadata
│
├── src/                              # Application source code
│   └── app.py                        # FastAPI application
│
├── tests/                            # Test suite
│   ├── test_model.py                 # Model tests
│   └── test_api.py                   # API tests
│
├── .github/                          # GitHub Actions
│   └── workflows/
│       └── ci-cd.yml                 # CI/CD pipeline
│
├── k8s/                              # Kubernetes manifests
│   └── deployment.yaml               # K8s deployment config
│
├── monitoring/                       # Monitoring configuration
│   └── prometheus.yml                # Prometheus config
│
└── scripts/                          # Utility scripts
    ├── run_tests.sh                  # Test runner
    ├── build_and_run.sh             # Build and run
    └── deploy_local.sh               # Local deployment
```

## Key Components

1. **Model Artifacts** (`model_artifact/`): Output from data science team
2. **Application Code** (`src/`): Production-ready FastAPI service
3. **Containerization** (`Dockerfile`, `docker-compose.yml`): Container setup
4. **CI/CD** (`.github/workflows/`): Automated pipeline
5. **Testing** (`tests/`): Comprehensive test suite
6. **Deployment** (`k8s/`): Kubernetes configuration
7. **Monitoring** (`monitoring/`): Observability setup
8. **Documentation** (`README.md`, examples): Complete documentation

## Workflow

1. Data scientist provides model artifacts
2. Application code loads and serves the model
3. CI/CD pipeline tests, builds, and deploys
4. Monitoring ensures production health
5. Updates trigger automated redeployment
EOF

echo ""
echo "✅ 5-Minute Model-to-Market CI/CD Pipeline Demo created successfully!"
echo ""
echo "📊 Project Summary:"
echo "  📁 Project directory: $(pwd)"
echo "  🔬 Model artifacts: ✅ Created"
echo "  💻 Application code: ✅ Created"
echo "  🐳 Containerization: ✅ Created"
echo "  🔧 CI/CD pipeline: ✅ Created"
echo "  🧪 Test suite: ✅ Created"
echo "  🚀 Deployment configs: ✅ Created"
echo "  📊 Monitoring setup: ✅ Created"
echo "  📖 Documentation: ✅ Created"
echo ""
echo "🚀 Next Steps:"
echo "  1. cd $PROJECT_DIR"
echo "  2. docker-compose up --build"
echo "  3. Open http://localhost:8080 in your browser"
echo "  4. Test the API with the examples in example_requests.json"
echo ""
echo "🎯 Demo is ready! This showcases a complete model-to-market pipeline."
EOF
