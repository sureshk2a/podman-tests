# Use Python 3.11 slim as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set Python to run in unbuffered mode and configure logging
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV CONTAINER=true

# Install build dependencies and podman
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    podman \
    && rm -rf /var/lib/apt/lists/*

# Set PYTHONPATH to include site-packages and application paths
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages:/app:/app/src

# Install required packages first
RUN pip install --no-cache-dir httpx fastapi uvicorn acp-sdk

# Copy project files
COPY pyproject.toml setup.py ./
COPY src/ src/

# Install project in editable mode
RUN pip install -e .

# Expose the port
EXPOSE 8001

# Run the router with output going to stdout
CMD ["python", "-u", "src/router/router.py"]