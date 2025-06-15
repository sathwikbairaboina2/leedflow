#!/bin/bash
docker build -t leedflow .
# Run FastAPI app
docker-compose up -d  
