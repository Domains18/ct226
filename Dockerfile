# Telegram Contact Importer - Dockerfile
FROM python:3.11-slim

# Metadata
LABEL maintainer="Domains18"
LABEL description="Telegram Contact Importer CLI"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libssl-dev \
        && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Install the application
RUN pip install --no-cache-dir -e .

# Create directories for data and logs
RUN mkdir -p /app/data /app/logs

# Create a non-root user
RUN useradd -m -u 1000 telegramuser && \
    chown -R telegramuser:telegramuser /app

USER telegramuser

# Set volume mount points
VOLUME ["/app/data", "/app/logs"]

# Default command
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
