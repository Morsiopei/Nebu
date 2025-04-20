#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Starting Development Setup ---"

# 1. Ensure Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker does not seem to be running. Please start Docker and try again."
  exit 1
fi

# 2. Copy .env file if it doesn't exist
if [ ! -f .env ]; then
  echo "Copying .env.example to .env..."
  cp .env.example .env
  echo "IMPORTANT: Please review and update the .env file with your secrets!"
  # Optionally exit here to force user review:
  # echo "Exiting script. Please configure .env before running again."
  # exit 1
fi

# 3. Build Docker images
echo "Building Docker images..."
docker-compose build

# 4. Start database container first and wait for it to be healthy
echo "Starting database container..."
docker-compose up -d postgres_db
echo "Waiting for database to be healthy..."
# Loop based on health check defined in docker-compose.yml
max_wait=60
current_wait=0
while [ "$(docker inspect --format='{{.State.Health.Status}}' multifaceted_postgres)" != "healthy" ]; do
  if [ $current_wait -ge $max_wait ]; then
    echo "Error: Timed out waiting for database to become healthy."
    docker-compose logs postgres_db # Show logs for debugging
    exit 1
  fi
  printf '.'
  sleep 2
  current_wait=$((current_wait + 2))
done
echo "\nDatabase is healthy."

# 5. Start other backend services (without frontend for now)
echo "Starting backend services..."
# Start services needed for migrations first
docker-compose up -d auth_service finance_service # Add other backend services here

# 6. Apply Database Migrations
echo "Applying migrations for auth_service..."
docker-compose exec auth_service python manage.py migrate --noinput

echo "Applying migrations for finance_service..."
docker-compose exec finance_service python manage.py migrate --noinput

# Add migration commands for other services as needed
# echo "Applying migrations for health_service..."
# docker-compose exec health_service python manage.py migrate --noinput

echo "Migrations applied."

# 7. Start remaining services (including frontend)
echo "Starting remaining services (including frontend)..."
docker-compose up -d

echo "--- Development Setup Complete ---"
echo "Application should be accessible shortly."
echo "Frontend: http://localhost:3000 (or as configured)"
echo "API Gateway: http://localhost:8000"
echo "----------------------------------"
echo "To stop the services, run: docker-compose down"
echo "To view logs, run: docker-compose logs -f [service_name] (e.g., finance_service)"
