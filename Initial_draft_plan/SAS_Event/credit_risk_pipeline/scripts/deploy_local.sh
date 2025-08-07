#!/bin/bash
echo "Deploying locally with Docker..."
docker build -t credit-risk-model .
docker run -p 8080:8080 credit-risk-model
