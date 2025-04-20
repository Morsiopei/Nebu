# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies if needed (e.g., for psycopg2)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Copy entrypoint script and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose the port the app runs on (internal to Docker)
EXPOSE 8002

# Run entrypoint script when container launches
# The script should handle migrations and start the server (e.g., gunicorn)
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command if entrypoint doesn't exec the final process (less common)
# CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8002"]
