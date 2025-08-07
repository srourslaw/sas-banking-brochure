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
