#!/bin/bash

echo "Starting Document Generator Backend..."
echo ""

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Start the server
echo "Backend server starting on http://localhost:8000"
echo "API docs available at http://localhost:8000/api/v1/docs"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
