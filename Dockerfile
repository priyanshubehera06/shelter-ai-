# Multi-stage or optimized single-stage Dockerfile for ShelterAI FastAPI Backend on Railway / Cloud
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if required for numerical computation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application backend, engine, data, and tests
COPY engine/ ./engine/
COPY data/ ./data/
COPY backend/ ./backend/

# Expose default HTTP port
EXPOSE 8000

# Environment defaults
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Run Uvicorn listening on dynamically assigned Railway / Container $PORT
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
