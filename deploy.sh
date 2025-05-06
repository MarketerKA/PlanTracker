#!/bin/bash
set -e

# Default mode is deploy
MODE=${1:-deploy}
VERSION=${2:-latest}

# Create a directory to store deployment history
mkdir -p .deployment_history

# Function to save the current deployment state
save_deployment_state() {
  TIMESTAMP=$(date +%Y%m%d%H%M%S)
  DEPLOYED_FRONTEND=$(docker inspect plantracker-frontend --format='{{.Config.Image}}' || echo "not-found")
  DEPLOYED_BACKEND=$(docker inspect plantracker-backend --format='{{.Config.Image}}' || echo "not-found")
  
  echo "{\"timestamp\": \"$TIMESTAMP\", \"frontend\": \"$DEPLOYED_FRONTEND\", \"backend\": \"$DEPLOYED_BACKEND\"}" > .deployment_history/deploy_$TIMESTAMP.json
  
  # Keep only the last 10 deployments
  ls -t .deployment_history/deploy_*.json | tail -n +11 | xargs -r rm
  
  echo "Deployment state saved: $TIMESTAMP"
}

# Function to list all available deployment states
list_deployments() {
  echo "Available deployments (most recent first):"
  for file in $(ls -t .deployment_history/deploy_*.json); do
    TIMESTAMP=$(basename "$file" | sed 's/deploy_\(.*\)\.json/\1/')
    FRONTEND=$(grep -o '"frontend": "[^"]*"' "$file" | cut -d'"' -f4)
    BACKEND=$(grep -o '"backend": "[^"]*"' "$file" | cut -d'"' -f4)
    echo "- $TIMESTAMP : Frontend=$FRONTEND, Backend=$BACKEND"
  done
}

# Function to rollback to a specific version
rollback() {
  if [ ! -f ".deployment_history/deploy_$VERSION.json" ]; then
    echo "Error: Deployment version $VERSION not found!"
    list_deployments
    exit 1
  fi
  
  FRONTEND=$(grep -o '"frontend": "[^"]*"' ".deployment_history/deploy_$VERSION.json" | cut -d'"' -f4)
  BACKEND=$(grep -o '"backend": "[^"]*"' ".deployment_history/deploy_$VERSION.json" | cut -d'"' -f4)
  
  echo "Rolling back to version $VERSION:"
  echo "Frontend: $FRONTEND"
  echo "Backend: $BACKEND"
  
  # Update .env file with the specific versions
  sed -i "s|^FRONTEND_VERSION=.*|FRONTEND_VERSION=$FRONTEND|g" .env
  sed -i "s|^BACKEND_VERSION=.*|BACKEND_VERSION=$BACKEND|g" .env
  
  # Restart services
  docker-compose down
  docker-compose up -d
  
  echo "Rollback to version $VERSION completed"
}

case "$MODE" in
  deploy)
    echo "Starting deployment..."
    
    # Save current state before new deployment
    if [ "$(docker ps -q -f name=plantracker-frontend)" ] && [ "$(docker ps -q -f name=plantracker-backend)" ]; then
      save_deployment_state
    fi
    
    # Make sure .env has latest tags
    grep -q "^FRONTEND_VERSION=" .env || echo "FRONTEND_VERSION=latest" >> .env
    grep -q "^BACKEND_VERSION=" .env || echo "BACKEND_VERSION=latest" >> .env
    sed -i "s|^FRONTEND_VERSION=.*|FRONTEND_VERSION=latest|g" .env
    sed -i "s|^BACKEND_VERSION=.*|BACKEND_VERSION=latest|g" .env
    
    # Pull the latest images
    docker-compose pull
    
    # Restart the services
    docker-compose down
    docker-compose up -d
    
    # Clean up old images
    docker image prune -af --filter "until=24h"
    
    echo "Deployment completed successfully!"
    ;;
    
  rollback)
    if [ -z "$VERSION" ]; then
      echo "Error: Version parameter is required for rollback"
      list_deployments
      exit 1
    fi
    rollback
    ;;
    
  list)
    list_deployments
    ;;
    
  *)
    echo "Usage: $0 [deploy|rollback|list] [version]"
    echo "  deploy: Deploy the latest version (default)"
    echo "  rollback VERSION: Rollback to a specific version"
    echo "  list: List all available deployment versions"
    exit 1
    ;;
esac 