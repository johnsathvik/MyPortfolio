#!/bin/bash
set -e # Exit immediately if a command fails

# 1. NAVIGATE TO PROJECT DIRECTORY (CRITICAL FIX)
# This ensures we are in the folder where appspec.yml put the files
cd /home/ubuntu/MyPortfolio

# 2. Stop existing containers
echo "Stopping and removing existing Docker containers..."
docker compose down -v || true 

# 3. Build and start new containers
echo "Building and starting new Docker containers..."
docker compose up -d --build

echo "Deployment complete."