#!/bin/bash

# Script to securely copy .env.production files to VPS
# Run this after pushing code to GitHub

echo "================================================"
echo "Copy Environment Files to VPS"
echo "================================================"

# Check if .env.production exists locally
if [ ! -f ".env.production" ]; then
    echo "Error: .env.production not found in current directory"
    exit 1
fi

# VPS details
VPS_HOST="api.rapiddocs.io"
VPS_USER="root"
VPS_BACKEND_DIR="/home/docgen/backend"

echo "Copying .env.production to VPS..."

# Copy the file
scp .env.production ${VPS_USER}@${VPS_HOST}:${VPS_BACKEND_DIR}/.env.production

if [ $? -eq 0 ]; then
    echo "✅ Successfully copied .env.production to VPS"
    echo ""
    echo "Next steps:"
    echo "1. SSH into VPS: ssh ${VPS_USER}@${VPS_HOST}"
    echo "2. Run deployment: cd ${VPS_BACKEND_DIR} && ./deploy-auth.sh"
    echo "3. Save the initial referral key shown in the output"
    echo "4. Register first admin at https://api.rapiddocs.io/register"
else
    echo "❌ Failed to copy .env.production to VPS"
    echo "Please copy manually using:"
    echo "scp .env.production ${VPS_USER}@${VPS_HOST}:${VPS_BACKEND_DIR}/"
fi