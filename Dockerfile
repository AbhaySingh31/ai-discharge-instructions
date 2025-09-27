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
RUN cd backend && pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy frontend package.json and install Node dependencies
COPY frontend/package*.json /app/frontend/
RUN cd frontend && npm install

# Copy all application code
COPY . /app/

# Build frontend
RUN cd frontend && npm run build

# Set up database and seed data
RUN cd backend && python seed_database.py || echo "Database seeding failed, continuing..."
RUN cd backend && python simple_migration.py || echo "Migration failed, continuing..."

# Expose port
EXPOSE $PORT

# Start the backend server
CMD cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
