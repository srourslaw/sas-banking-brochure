#!/bin/bash
echo "Building and running the application..."
docker-compose down
docker-compose up --build
