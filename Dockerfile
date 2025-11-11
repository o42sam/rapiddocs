# Multi-stage build for doc-gen application
# This Dockerfile builds both frontend and backend in a single container

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Setup backend
# Use Python 3.10 with stable OpenSSL 1.1.1 for MongoDB Atlas compatibility
FROM python:3.10-slim-bullseye

# Install system dependencies including SSL certificates and OpenSSL
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    ca-certificates \
    libssl-dev \
    openssl \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ ./

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./static

# Create necessary directories
RUN mkdir -p uploads generated_pdfs logs

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV OPENSSL_CONF=/etc/ssl/

# Run the application
# Use shell form to allow environment variable substitution
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
