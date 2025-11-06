#!/bin/bash
echo "Building Docker container..."
docker-compose build

echo "Starting services..."
docker-compose up -d

echo "Waiting for startup..."
sleep 10

echo "Running tests..."
docker-compose run --rm feature-tester

echo "Container status:"
docker-compose ps

echo "Stopping containers..."
docker-compose down
