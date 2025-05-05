# CI/CD Pipeline Setup for PlanTracker

This document describes the CI/CD pipeline configuration for the PlanTracker project.

## Workflow Structure

The project uses three separate GitHub Actions workflows:

1. **Backend CI/CD** (main.yml):
   - Triggered when changes are made to backend code
   - Runs Python dependency installation, linting, tests, and SonarCloud scans

2. **Frontend CI** (frontend.yml):
   - Triggered when changes are made to frontend code
   - Runs Node.js dependency installation, linting, and build verification

3. **Docker Build & Push** (docker-build.yml):
   - Triggered when Dockerfiles or docker-compose.yml are modified
   - Builds and pushes Docker images to Docker Hub

## Overview

The CI/CD pipelines collectively:
1. Install dependencies
2. Run linting checks (flake8 for backend, ESLint for frontend)
3. Execute unit tests with pytest (backend)
4. Perform SonarCloud scans for code quality (backend)
5. Build and push Docker images to Docker Hub (when Dockerfiles change)

## Required Secrets

You need to set up the following secrets in your GitHub repository:

- `SONAR_TOKEN`: Token for SonarCloud integration
- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Your Docker Hub access token

## Setting Up Secrets

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Click on "New repository secret"
4. Add each of the required secrets

## SonarCloud Setup

1. Create an account on [SonarCloud](https://sonarcloud.io/)
2. Create an organization (or use an existing one)
3. Create a project with the key `MarketerKA_PlanTracker` (or update the key in the workflow file)
4. Generate a token and add it as the `SONAR_TOKEN` secret in GitHub

## Docker Hub Setup

1. Create an account on [Docker Hub](https://hub.docker.com/)
2. Generate an access token in your Docker Hub account settings
3. Add your username as `DOCKERHUB_USERNAME` and token as `DOCKERHUB_TOKEN` in GitHub secrets

## Running the Pipeline

The pipeline runs automatically on:
- Every push to the `main` branch
- Every pull request to the `main` branch

Only successful builds on the `main` branch will trigger Docker image builds and pushes.

## Docker Images

The pipeline builds and pushes two Docker images:
- `<your-username>/plantracker-backend:latest`
- `<your-username>/plantracker-frontend:latest`

## Local Development with Docker

You can run the application locally using Docker Compose:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## Container Structure

- **Backend**: Python FastAPI application running on port 8000
- **Frontend**: React application served via Nginx on port 80 