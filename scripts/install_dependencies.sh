#!/bin/bash

cd /home/ubuntu/MyPortfolio

# Create venv if not exists
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip
pip install -r PortfolioMain/requirements.txt
pip install -r admin/requirements.txt

# Copy systemd service file
sudo cp PortfolioMain/portfolioapp.service /etc/systemd/system/portfolioapp.service
sudo systemctl daemon-reload