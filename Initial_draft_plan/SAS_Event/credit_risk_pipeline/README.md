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
