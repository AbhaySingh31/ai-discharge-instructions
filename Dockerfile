# Backend-only Dockerfile for Railway
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ .

# Set up database and seed data (with error handling)
RUN python seed_data.py || echo "Database seeding failed, continuing..."
RUN python simple_migration.py || echo "Migration failed, continuing..."

# Expose port
EXPOSE $PORT

# Start the application
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
