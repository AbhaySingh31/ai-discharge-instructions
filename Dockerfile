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

# Copy and install backend dependencies
COPY backend/requirements.txt ./backend/
WORKDIR /app/backend
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy and install frontend dependencies
WORKDIR /app
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm install

# Copy all source code
WORKDIR /app
COPY . .

# Build frontend
WORKDIR /app/frontend
RUN npm run build

# Setup backend database - commented out for now
WORKDIR /app/backend
# RUN python seed_database.py || true
# RUN python simple_migration.py || true

# Set final working directory and start command
WORKDIR /app/backend
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
