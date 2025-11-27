#!/bin/bash
cd /home/ubuntu/MyPortfolio
source venv/bin/activate

sudo systemctl restart portfolioapp
sudo systemctl enable portfolioapp