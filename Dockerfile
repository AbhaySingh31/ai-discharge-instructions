# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt /app/backend/
WORKDIR /app/backend
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy frontend package.json and install Node dependencies
WORKDIR /app
COPY frontend/package*.json /app/frontend/
WORKDIR /app/frontend
RUN npm install

# Copy all application code
WORKDIR /app
COPY . /app/

# Build frontend
WORKDIR /app/frontend
RUN npm run build

# Set up database and seed data
WORKDIR /app/backend
RUN python seed_database.py || echo "Database seeding failed, continuing..."
RUN python simple_migration.py || echo "Migration failed, continuing..."

# Expose port
EXPOSE $PORT

# Start the backend server
WORKDIR /app/backend
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
