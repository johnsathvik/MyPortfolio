#!/bin/bash
set -e

cd /home/ubuntu/MyPortfolio || exit

echo "Stopping old containers..."
docker compose down -v || true

echo "Rebuilding and starting docker containers..."
docker compose up -d --build

echo "Deployment complete."
