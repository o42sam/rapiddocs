#!/bin/bash

# Build script for Railway deployment
# This script builds the frontend and copies it to backend/static

echo "🔨 Starting build process..."

# Build frontend
echo "📦 Building frontend..."
cd frontend
npm install
npm run build

# Copy built files to backend/static
echo "📁 Copying frontend to backend/static..."
cd ..
rm -rf backend/static
cp -r frontend/dist backend/static

echo "✅ Build complete!"
echo "Frontend built and copied to backend/static"
