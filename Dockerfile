# Lightweight Dockerfile for Sentiment Analyzer
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app/app.py
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV PIP_NO_CACHE_DIR=1

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements-docker.txt ./requirements.txt

# Install Python dependencies with minimal footprint (CPU-only PyTorch)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (excluding large model files)
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser config.py logging_config.py ./

# Note: Yelp_Model/ is excluded to save storage - will use fallback model

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/model_cache && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Expose port
EXPOSE 5000

# Default command
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
