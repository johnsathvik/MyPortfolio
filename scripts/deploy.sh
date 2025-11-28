#!/bin/bash
set -e

# Navigate to the project directory
cd /home/ubuntu/MyPortfolio

# 1. Build new images (This happens while the old site is still running!)
echo "Building new Docker images..."
docker-compose build

# 2. Stop old containers and start new ones
echo "Deploying new containers..."
docker-compose down
docker-compose up -d

# 3. Clean up space (optional)
docker image prune -f