#!/bin/bash
set -e # CRITICAL: Script will now fail the pipeline if any command fails

# 1. NAVIGATE TO PROJECT DIRECTORY (CRITICAL FIX)
# We must move to the destination folder where appspec.yml put the files
cd /home/ubuntu/MyPortfolio 

# 2. Stop and remove existing containers 
echo "Stopping and removing existing Docker containers..."
docker compose down -v || true 

# 3. Build and start new containers
echo "Building and starting new Docker containers..."
# --build ensures the new code is used
docker compose up -d --build

echo "Deployment complete."