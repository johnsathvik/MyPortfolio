# Portfolio Main App Startup Script
# This script sets up the correct Python path and runs the Flask application

# Set the project root in PYTHONPATH so Python can find the config module
$env:PYTHONPATH = "d:\Disk\MyPortfolio"

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# Run the Flask application
python PortfolioMain\app.py
