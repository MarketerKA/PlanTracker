#!/bin/bash
set -e

# Pull the latest images
docker-compose pull

# Restart the services
docker-compose down
docker-compose up -d

# Clean up old images
docker image prune -af 