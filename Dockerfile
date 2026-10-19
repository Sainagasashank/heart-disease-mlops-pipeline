# Slim production runtime image for Heart Disease Serving API.
FROM python:3.12-slim AS runtime

# Set security and performance environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# Install curl for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create non-root application user for container security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy application source code and serialized model artifact
COPY src/ ./src/
COPY models/ ./models/

# Set ownership to appuser
RUN chown -R appuser:appuser ${APP_HOME}
USER appuser

# Expose HTTP serving port
EXPOSE 8000

# Container healthcheck probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch production Uvicorn server
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
