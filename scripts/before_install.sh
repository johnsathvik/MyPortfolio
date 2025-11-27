#!/bin/bash
sudo systemctl stop portfolioapp || true
sudo rm -rf /home/ubuntu/MyPortfolio
sudo mkdir -p /home/ubuntu/MyPortfolio