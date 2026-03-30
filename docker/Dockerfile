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

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Install Playwright for browser automation (can be removed if not needed)
RUN pip install --no-cache-dir playwright && \
    playwright install chromium

# Create necessary directories
RUN mkdir -p /app/workdir /app/tmp

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app:$PYTHONPATH

# Load .env at runtime
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'if [ -f .env ]; then' >> /entrypoint.sh && \
    echo '  set -a' >> /entrypoint.sh && \
    echo '  source .env' >> /entrypoint.sh && \
    echo '  set +a' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Default command - can be overridden
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "nano.main"]
