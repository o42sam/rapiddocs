#!/bin/bash

echo "Starting Document Generator Frontend..."
echo ""

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Error: node_modules not found. Please run setup.sh first."
    exit 1
fi

# Start the development server
echo "Frontend server starting on http://localhost:5173"
echo ""

npm run dev
