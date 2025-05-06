FROM python:3.14-rc-alpine3.20 AS build

WORKDIR /app

# Install system dependencies 
RUN apk add --no-cache \
    build-base \
    curl

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
FROM python:3.14-rc-alpine3.20

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install only needed runtime dependencies
RUN apk add --no-cache curl

# Create non-root user with specific UID/GID
RUN addgroup -g 1001 appuser && adduser -u 1001 -G appuser -D appuser

# Copy dependencies from build stage
COPY --from=build /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
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

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 