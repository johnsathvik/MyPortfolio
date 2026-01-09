#!/bin/bash
set -e

cd /home/ubuntu/MyPortfolio
git pull origin main

source .venv/bin/activate
pip install -r requirements.txt

#git reset --hard
#git clean -fd
#git pull origin main


sudo systemctl restart portfolio-main
sudo systemctl restart portfolio-admin