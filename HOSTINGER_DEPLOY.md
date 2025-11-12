# Deploy RapidDocs to Hostinger VPS

Complete guide to deploy your FastAPI + MongoDB application to Hostinger VPS using cryptocurrency payment.

## Prerequisites

- ✅ Hostinger VPS account (can pay with Bitcoin/crypto)
- ✅ Domain name (rapiddocs.io - already configured)
- ✅ MongoDB Atlas account (already set up)
- ✅ Your application code (already ready)

---

## Step 1: Purchase Hostinger VPS

### 1.1 Choose a Plan

**Recommended Plan**: KVM 1 VPS
- **Price**: $3.99/month (first purchase)
- **Specs**:
  - 1 vCPU Core
  - 4 GB RAM
  - 50 GB NVMe Storage
  - 1 TB Bandwidth
- **Perfect for**: Your FastAPI app + Docker

**Link**: https://www.hostinger.com/vps-hosting

### 1.2 Pay with Cryptocurrency

1. Go to checkout
2. Select **CoinGate** as payment method
3. Choose your cryptocurrency:
   - Bitcoin (BTC)
   - Ethereum (ETH)
   - Litecoin (LTC)
   - USDC/USDT stablecoins
   - 70+ other options
4. Complete payment
5. Wait for blockchain confirmation (5-30 minutes)

### 1.3 Access VPS Details

After payment confirmation:
1. Check email for VPS access details
2. You'll receive:
   - **IP Address**: `xxx.xxx.xxx.xxx`
   - **SSH Port**: Usually 22
   - **Root Password**: (or SSH key)
3. Save these credentials securely

---

## Step 2: Initial Server Setup

### 2.1 Connect to Your VPS

```bash
# From your local machine
ssh root@YOUR_VPS_IP

# Enter password when prompted
```

### 2.2 Update System

```bash
# Update package lists
apt update

# Upgrade installed packages
apt upgrade -y

# Install essential tools
apt install -y curl git wget nano ufw
```

### 2.3 Set Up Firewall

```bash
# Allow SSH (important - don't lock yourself out!)
ufw allow 22/tcp

# Allow HTTP
ufw allow 80/tcp

# Allow HTTPS
ufw allow 443/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

### 2.4 Create Non-Root User (Optional but Recommended)

```bash
# Create new user
adduser deploy

# Add to sudo group
usermod -aG sudo deploy

# Switch to new user
su - deploy
```

---

## Step 3: Install Docker

### 3.1 Install Docker Engine

```bash
# Download Docker installation script
curl -fsSL https://get.docker.com -o get-docker.sh

# Run installation script
sudo sh get-docker.sh

# Add current user to docker group (avoid using sudo)
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Verify installation
docker --version
docker run hello-world
```

### 3.2 Install Docker Compose

```bash
# Install Docker Compose
sudo apt install -y docker-compose

# Verify installation
docker-compose --version
```

---

## Step 4: Clone and Configure Your Application

### 4.1 Clone Repository

```bash
# Navigate to home directory
cd ~

# Clone your repository
git clone https://github.com/o42sam/rapiddocs.git

# Enter project directory
cd rapiddocs
```

### 4.2 Set Up Environment Variables

```bash
# Navigate to backend directory
cd backend

# Create production .env file
nano .env
```

**Paste the following** (update with your actual values):

```bash
# Application Settings
APP_NAME=RapidDocs
APP_ENV=production
DEBUG=False
API_PREFIX=/api/v1

# MongoDB Atlas (your existing connection)
MONGODB_URL=mongodb+srv://USERNAME:PASSWORD@cluster.mongodb.net/
MONGODB_DB_NAME=docgen
DISABLE_MONGODB=False

# Hugging Face API
HUGGINGFACE_API_KEY=hf_your_actual_key_here
TEXT_GENERATION_MODEL=meta-llama/Llama-3.2-3B-Instruct
IMAGE_GENERATION_MODEL=black-forest-labs/FLUX.1-schnell

# File Storage
UPLOAD_DIR=./uploads
PDF_OUTPUT_DIR=./generated_pdfs
MAX_UPLOAD_SIZE=5242880

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (update with your actual domain)
CORS_ORIGINS=https://rapiddocs.io,https://www.rapiddocs.io

# Bitcoin Payment (if using)
BITCOIN_NETWORK=mainnet
BITCOIN_FORWARD_ADDRESS=your_bitcoin_address_here
BITCOIN_CONFIRMATION_BLOCKS=1
```

**Save and exit**: `Ctrl+X`, then `Y`, then `Enter`

### 4.3 Verify MongoDB Connection

```bash
# Test MongoDB connection from VPS
cd ~/rapiddocs/backend
python3 -m pip install motor python-dotenv
python3 -c "
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    await client.admin.command('ping')
    print('✅ MongoDB connected successfully!')
    client.close()

asyncio.run(test())
"
```

---

## Step 5: Build and Run Docker Container

### 5.1 Build Docker Image

```bash
# Navigate to project root
cd ~/rapiddocs

# Build Docker image (this takes 5-10 minutes)
docker build -t rapiddocs:latest .

# Verify image was created
docker images | grep rapiddocs
```

### 5.2 Run Docker Container

```bash
# Run container in background
docker run -d \
  --name rapiddocs \
  --restart unless-stopped \
  -p 8000:8000 \
  -v ~/rapiddocs/backend/uploads:/app/uploads \
  -v ~/rapiddocs/backend/generated_pdfs:/app/generated_pdfs \
  --env-file ~/rapiddocs/backend/.env \
  rapiddocs:latest

# Check if container is running
docker ps

# View logs
docker logs rapiddocs

# Follow logs in real-time
docker logs -f rapiddocs
```

### 5.3 Test Application

```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return: {"status":"healthy"}

# Test API endpoint
curl http://localhost:8000/api/v1/docs
```

---

## Step 6: Set Up Nginx Reverse Proxy

### 6.1 Install Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Start Nginx
sudo systemctl start nginx

# Enable Nginx to start on boot
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

### 6.2 Configure Nginx for Your Domain

```bash
# Create Nginx configuration file
sudo nano /etc/nginx/sites-available/rapiddocs.io
```

**Paste the following configuration**:

```nginx
server {
    listen 80;
    server_name rapiddocs.io www.rapiddocs.io;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Increase upload size for logo uploads
    client_max_body_size 10M;

    # Proxy to FastAPI application
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts for long-running requests (document generation)
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
```

**Save and exit**: `Ctrl+X`, then `Y`, then `Enter`

### 6.3 Enable Site

```bash
# Create symbolic link to enable site
sudo ln -s /etc/nginx/sites-available/rapiddocs.io /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## Step 7: Configure Domain DNS

### 7.1 Update DNS Records

Go to your domain registrar (where you bought rapiddocs.io) and update DNS:

**A Records**:
```
Type: A
Name: @
Value: YOUR_VPS_IP_ADDRESS
TTL: 3600

Type: A
Name: www
Value: YOUR_VPS_IP_ADDRESS
TTL: 3600
```

**Wait 5-30 minutes** for DNS propagation.

### 7.2 Verify DNS

```bash
# Check if DNS is resolving
dig rapiddocs.io
dig www.rapiddocs.io

# Or use nslookup
nslookup rapiddocs.io
```

---

## Step 8: Set Up SSL Certificate (HTTPS)

### 8.1 Install Certbot

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx
```

### 8.2 Obtain SSL Certificate

```bash
# Get certificate (follow prompts)
sudo certbot --nginx -d rapiddocs.io -d www.rapiddocs.io

# Enter your email when prompted
# Agree to terms of service
# Choose whether to redirect HTTP to HTTPS (recommended: Yes)
```

### 8.3 Test Auto-Renewal

```bash
# Test certificate renewal
sudo certbot renew --dry-run

# Certbot will automatically renew before expiry
```

### 8.4 Verify HTTPS

Visit https://rapiddocs.io in your browser - should show secure connection!

---

## Step 9: Set Up Automatic Deployment (Optional)

### 9.1 Create Deployment Script

```bash
# Create deployment script
nano ~/deploy.sh
```

**Paste the following**:

```bash
#!/bin/bash

# RapidDocs Deployment Script
echo "🚀 Starting deployment..."

# Navigate to project directory
cd ~/rapiddocs

# Pull latest changes
echo "📥 Pulling latest code..."
git pull origin master

# Stop and remove old container
echo "🛑 Stopping old container..."
docker stop rapiddocs
docker rm rapiddocs

# Rebuild image
echo "🔨 Building new image..."
docker build -t rapiddocs:latest .

# Run new container
echo "▶️  Starting new container..."
docker run -d \
  --name rapiddocs \
  --restart unless-stopped \
  -p 8000:8000 \
  -v ~/rapiddocs/backend/uploads:/app/uploads \
  -v ~/rapiddocs/backend/generated_pdfs:/app/generated_pdfs \
  --env-file ~/rapiddocs/backend/.env \
  rapiddocs:latest

# Wait for container to start
sleep 5

# Check if container is running
if docker ps | grep -q rapiddocs; then
  echo "✅ Deployment successful!"
  docker logs --tail 20 rapiddocs
else
  echo "❌ Deployment failed!"
  docker logs rapiddocs
  exit 1
fi
```

**Save and exit**, then make executable:

```bash
chmod +x ~/deploy.sh
```

### 9.2 Deploy Updates

Whenever you push code changes:

```bash
# SSH into VPS
ssh root@YOUR_VPS_IP

# Run deployment script
~/deploy.sh
```

---

## Step 10: Monitoring and Maintenance

### 10.1 View Application Logs

```bash
# View last 100 lines
docker logs --tail 100 rapiddocs

# Follow logs in real-time
docker logs -f rapiddocs

# View logs with timestamps
docker logs -t rapiddocs
```

### 10.2 Restart Application

```bash
# Restart container
docker restart rapiddocs

# Or stop and start
docker stop rapiddocs
docker start rapiddocs
```

### 10.3 Check Resource Usage

```bash
# Check container stats
docker stats rapiddocs

# Check disk usage
df -h

# Check memory usage
free -h

# Check CPU load
top
```

### 10.4 Backup Important Data

```bash
# Backup MongoDB (from MongoDB Atlas dashboard)
# Already handled by MongoDB Atlas automatic backups

# Backup uploaded files
tar -czf uploads-backup-$(date +%Y%m%d).tar.gz ~/rapiddocs/backend/uploads

# Backup generated PDFs
tar -czf pdfs-backup-$(date +%Y%m%d).tar.gz ~/rapiddocs/backend/generated_pdfs

# Backup .env file
cp ~/rapiddocs/backend/.env ~/env-backup-$(date +%Y%m%d).env
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker logs rapiddocs

# Check if port is already in use
sudo lsof -i :8000

# Rebuild without cache
docker build --no-cache -t rapiddocs:latest .
```

### Can't Connect to MongoDB

```bash
# Test MongoDB connection from VPS
cd ~/rapiddocs/backend
python3 test_mongodb_atlas.py

# Check if MongoDB IP is whitelisted in Atlas
# Go to: MongoDB Atlas → Network Access → Add IP Address
# Add your VPS IP: YOUR_VPS_IP/32
```

### Site Not Loading

```bash
# Check Nginx status
sudo systemctl status nginx

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Test Nginx config
sudo nginx -t

# Check if Docker container is running
docker ps
```

### SSL Certificate Issues

```bash
# Renew certificate manually
sudo certbot renew

# Check certificate status
sudo certbot certificates

# Reconfigure Nginx
sudo certbot --nginx -d rapiddocs.io -d www.rapiddocs.io
```

---

## Useful Commands Reference

```bash
# Docker Commands
docker ps                          # List running containers
docker ps -a                       # List all containers
docker images                      # List images
docker logs rapiddocs              # View logs
docker exec -it rapiddocs bash     # Enter container shell
docker restart rapiddocs           # Restart container
docker stop rapiddocs              # Stop container
docker rm rapiddocs                # Remove container
docker rmi rapiddocs:latest        # Remove image

# Nginx Commands
sudo systemctl start nginx         # Start Nginx
sudo systemctl stop nginx          # Stop Nginx
sudo systemctl restart nginx       # Restart Nginx
sudo systemctl reload nginx        # Reload config
sudo nginx -t                      # Test config

# System Commands
htop                               # Monitor system resources
df -h                              # Check disk space
free -h                            # Check memory
ufw status                         # Check firewall status
```

---

## Cost Summary

**Monthly Costs**:
- VPS Hosting: $3.99/month (Hostinger KVM 1)
- MongoDB Atlas: $0/month (Free tier - 512MB)
- Domain: Already owned
- SSL Certificate: $0/month (Let's Encrypt - free)

**Total: ~$4/month** (pay with crypto!)

---

## Security Checklist

- ✅ Firewall configured (UFW)
- ✅ HTTPS enabled (SSL certificate)
- ✅ MongoDB connection encrypted (TLS)
- ✅ Environment variables secured (.env not in git)
- ✅ Non-root user created (optional)
- ✅ Automatic security updates enabled
- ✅ Strong passwords used
- ✅ MongoDB IP whitelist configured
- ✅ API rate limiting enabled (in FastAPI)

---

## Next Steps After Deployment

1. **Test the application**:
   - Visit https://rapiddocs.io
   - Try registering a new account
   - Test document generation
   - Test Bitcoin payment flow

2. **Monitor performance**:
   - Check logs regularly
   - Monitor resource usage
   - Set up uptime monitoring (optional)

3. **Scale if needed**:
   - Upgrade VPS plan if traffic increases
   - Consider adding Redis for caching
   - Set up CDN for static files

---

## Support

If you encounter issues:
1. Check troubleshooting section above
2. Review Docker logs: `docker logs rapiddocs`
3. Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
4. Verify MongoDB connection from Atlas dashboard
5. Contact Hostinger support if VPS issues

---

**Deployment Guide Version**: 1.0
**Last Updated**: November 11, 2025
**Tested On**: Hostinger VPS KVM 1, Ubuntu 22.04 LTS
