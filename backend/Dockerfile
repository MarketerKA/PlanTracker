FROM python:3.13.3-slim AS build

WORKDIR /app

# Install system dependencies 
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY tests/ ./tests/
COPY pyproject.toml .
COPY pytest.ini .
COPY .flake8 .

# Runtime stage (smaller image)
FROM python:3.13.3-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Update packages and install only needed runtime dependencies
# Use wget instead of curl for healthcheck
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y

# Create non-root user with specific UID/GID
RUN groupadd -r appuser -g 1001 && useradd -r -g appuser -u 1001 appuser

# Copy dependencies from build stage
COPY --from=build /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy application code
COPY --from=build /app/app ./app
COPY --from=build /app/pyproject.toml .

# Create a dummy .env file if needed
RUN echo "SECRET_KEY=\${SECRET_KEY:-dummy_secret_key}" > .env \
    && echo "TELEGRAM_BOT_TOKEN=\${TELEGRAM_BOT_TOKEN:-dummy_token}" >> .env

# Create data directory and set permissions
RUN mkdir -p /app/data && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port for the application
EXPOSE 8000

# Add healthcheck using wget instead of curl
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost:8000/health || exit 1

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 