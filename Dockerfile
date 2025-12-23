# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Playwright dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium only to save space)
RUN playwright install --with-deps chromium

# Copy application code
COPY . .

# Create data directory and subdirectories for writing
RUN mkdir -p /app/data /app/data/looker_cookies && chmod -R 777 /app/data

# Expose port 5000 (Flask default, but Cloud Run will use PORT env var)
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Run the application
# Cloud Run will set PORT environment variable, so we use it
CMD python -c "import os; from app import app; app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))"










