# =============================================================================
# Dockerfile:  Production Incubator Vault
# Project:     Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
# Description: Minimalist, high-security container for Streamlit deployment.
# =============================================================================

# 1. Use an official lightweight Python image
FROM python:3.11-slim

# 2. Set environment variables to optimize Python performance
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 3. Set work directory
WORKDIR /app

# 4. Install system dependencies for healthy image builds
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the entire project for clinical context
COPY . .

# 7. Expose the port (GCP Cloud Run defaults to 8080)
EXPOSE 8080

# 8. Start the Vault
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py"]
