#!/bin/sh

# Abort on any error
set -e

# --- Optional: Wait for Database ---
# This is a simple approach; more robust methods exist (e.g., dockerize-wait)
# Check if DB_HOST and DB_PORT environment variables are set
if [ -n "$DATABASE_HOST" ] && [ -n "$DATABASE_PORT" ]; then
    # Convert service name to IP address if needed, or rely on Docker DNS
    db_host=$DATABASE_HOST
    db_port=$DATABASE_PORT

    echo "Waiting for database at $db_host:$db_port..."

    # Loop until pg_isready reports success or timeout (e.g., 30 seconds)
    timeout=30
    while ! pg_isready -h "$db_host" -p "$db_port" -q -U "$POSTGRES_USER"; do
      timeout=$((timeout - 1))
      if [ $timeout -eq 0 ]; then
        echo "Timed out waiting for database."
        exit 1
      fi
      sleep 1
    done

    echo "Database is ready."
fi
# --- End Optional Wait ---


# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files (optional, depends on deployment strategy)
# echo "Collecting static files..."
# python manage.py collectstatic --noinput --clear

# Start the Gunicorn server (or Django dev server for debug)
echo "Starting Gunicorn server..."
# exec runs the command replacing the shell process, which is good practice for the main container command
exec gunicorn config.wsgi:application --bind 0.0.0.0:8002 --workers 3 --log-level info

# Alternatively, for development with DEBUG=True:
# echo "Starting Django development server..."
# exec python manage.py runserver 0.0.0.0:8002
