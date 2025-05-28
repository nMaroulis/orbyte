# Build stage for frontend
FROM node:18-alpine as frontend-builder

# Set working directory for frontend
WORKDIR /app/frontend

# Copy frontend files
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm ci

# Copy frontend source code
COPY frontend/ .

# Build frontend
RUN npm run build

# Production stage
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ .

# Copy built frontend files from builder
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Install backend in development mode
RUN pip install -e .

# Copy entrypoint script
COPY run.sh /app/
RUN chmod +x /app/run.sh

# Expose ports
EXPOSE 8000 5173

# Set the entrypoint
ENTRYPOINT ["/app/run.sh"]

# Default command
CMD []
