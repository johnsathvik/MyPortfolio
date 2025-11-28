# Start from a base Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
# This speeds up subsequent builds if requirements.txt hasn't changed
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files (like app.py, templates/, static/)
# The source path '.' refers to the './PortfolioMain' directory (the 'context' from docker-compose.yml)
COPY . . 

# Expose the port your Flask app is running on (5001 is common)
EXPOSE 5001

# The command to run the application when the container starts
CMD ["python", "app.py"]