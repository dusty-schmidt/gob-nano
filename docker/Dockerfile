# GOB-NANO - Ultra-minimal AI Agent for Edge Devices
# Based on python:3.12-slim for minimal footprint

FROM python:3.12-slim

LABEL maintainer="dusty-schmidt"
LABEL description="Ultra-minimal AI agent framework for edge devices (4-8GB RAM)"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only project metadata files first
COPY pyproject.toml MANIFEST.in ./
COPY README.md ./

# Install build dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy source code
COPY src ./src
COPY tests ./tests
COPY config ./config

# Install package in editable mode
# Install package in editable mode with dev dependencies for testing
RUN pip install --no-cache-dir -e ".[dev]"

# Create necessary directories
RUN mkdir -p /app/workdir /app/tmp /app/docker

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app:$PYTHONPATH

# Create entrypoint script to load .env
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'if [ -f .env ]; then' >> /entrypoint.sh && \
    echo '  set -a' >> /entrypoint.sh && \
    echo '  source .env' >> /entrypoint.sh && \
    echo '  set +a' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Copy entrypoint script
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Default entrypoint and command
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "-m", "src.gob.main"]
