FROM python:3.11-slim

# Prevent interactive prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install essential system dependencies needed for execution
RUN apt-get update && \
    apt-get install -y --no-install-recommends jq git curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install project dependencies
RUN pip install --no-cache-dir -e .

# Create non-root user for safer execution (optional but recommended)
RUN groupadd --system gobuser && useradd --system -g gobuser gobuser

# Security: run as non-root
USER gobuser

# Default entrypoint (overridable by docker-compose run command)
ENTRYPOINT ["python", "-m", "gob.run_gob"]
