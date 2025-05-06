FROM python:3.11-slim

WORKDIR /app

# Install system dependencies 
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

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

# Create a dummy .env file if needed
RUN echo "SECRET_KEY=\${SECRET_KEY:-dummy_secret_key}" > .env \
    && echo "TELEGRAM_BOT_TOKEN=\${TELEGRAM_BOT_TOKEN:-dummy_token}" >> .env

# Set ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port for the application
EXPOSE 8000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 