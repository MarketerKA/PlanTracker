#!/bin/bash
set -e

echo "Starting test deployment..."
docker-compose -f docker-compose.test.yml down -v || true
docker-compose -f docker-compose.test.yml build
docker-compose -f docker-compose.test.yml up -d

echo "Waiting for services to start..."
sleep 10

echo "Checking if containers are running:"
docker ps

echo "Testing NGINX connectivity..."
curl -I http://localhost:8080 || echo "Failed to connect to NGINX"

echo "Testing API connectivity through NGINX..."
curl -I http://localhost:8080/api/ || echo "Failed to connect to API"

echo "Checking container logs:"
echo "NGINX logs:"
docker logs plantracker-nginx-test

echo "Frontend logs:"
docker logs plantracker-frontend-test

echo "Backend logs:"
docker logs plantracker-backend-test

echo "Test complete! Cleaning up..."
docker-compose -f docker-compose.test.yml down -v

echo "Done!" 