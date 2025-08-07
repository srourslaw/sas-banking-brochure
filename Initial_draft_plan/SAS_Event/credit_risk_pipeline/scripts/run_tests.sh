#!/bin/bash
echo "Running all tests..."
python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term
echo "Coverage report generated in htmlcov/"
