# Mini-Agent-Zero Nano
# Ultra-minimal Docker container for edge devices

FROM python:3.12-slim

# Set working directory
WORKDIR /a0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install minimal Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install playwright
RUN playwright install chromium

# Create directories
RUN mkdir -p /a0/workdir /a0/tmp /a0/agents /a0/tools /a0/helpers/memory

# Copy application code
COPY . /a0/

# Run agent
CMD ["python", "main.py"]
