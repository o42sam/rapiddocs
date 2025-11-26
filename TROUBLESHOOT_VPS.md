# Troubleshooting VPS Deployment - Site Not Reachable

Based on your deployment output, everything looks good:
- ✅ Docker container is running
- ✅ Nginx is running
- ✅ SSL certificate is installed
- ❌ Site still not reachable

## Quick Diagnostic Steps

### 1. Check Docker Container Logs (Full Output)

```bash
# View full container logs
docker logs rapiddocs

# Check if there are any errors
docker logs rapiddocs 2>&1 | grep -i error

# Check if app started successfully
docker logs rapiddocs 2>&1 | grep -i "Application startup complete"
```

**Expected output**:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Test Container Directly

```bash
# Test health endpoint from VPS
curl http://localhost:8000/health

# Should return: {"status":"healthy"}

# If it doesn't work, container has issues
```

### 3. Check Nginx Configuration

```bash
# View Nginx config
cat /etc/nginx/sites-available/rapiddocs.io

# Test Nginx can reach backend
curl -I http://localhost:8000
```

### 4. Check DNS Resolution

```bash
# Check if DNS is pointing to your VPS
dig rapiddocs.io +short

# Should return your VPS IP address
```

### 5. Check Firewall

```bash
# Check if ports are open
sudo ufw status

# Should show:
# 22/tcp ALLOW
# 80/tcp ALLOW
# 443/tcp ALLOW
```

### 6. Check if Nginx is Listening

```bash
# Check what's listening on port 80 and 443
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Should show nginx processes
```

## Common Issues and Fixes

### Issue 1: Container Not Starting Properly

**Symptom**: `docker ps` shows container but `curl localhost:8000` fails

**Fix**:
```bash
# Check container logs for errors
docker logs rapiddocs

# Common error: Missing environment variables
# Solution: Check .env file exists and has correct values
ls -la ~/rapiddocs/backend/.env

# If .env is missing or incomplete, recreate it:
nano ~/rapiddocs/backend/.env
# Add all required environment variables
```

### Issue 2: MongoDB Connection Failed

**Symptom**: Container logs show MongoDB connection errors

**Fix**:
```bash
# Check MongoDB Atlas Network Access
# Go to: https://cloud.mongodb.com
# Network Access → IP Access List
# Add your VPS IP address

# Get your VPS IP
curl ifconfig.me

# Add this IP to MongoDB Atlas whitelist
```

### Issue 3: Port 8000 Not Accessible

**Symptom**: Container runs but `curl localhost:8000` times out

**Fix**:
```bash
# Check if container port is correctly mapped
docker ps
# Should show: 0.0.0.0:8000->8000/tcp

# Restart container if needed
docker restart rapiddocs

# Check container is actually listening
docker exec rapiddocs netstat -tlnp | grep 8000
```

### Issue 4: Nginx Can't Connect to Backend

**Symptom**: Nginx shows "502 Bad Gateway" or "Connection refused"

**Fix**:
```bash
# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Common issue: Nginx trying to connect before container is ready
# Solution: Wait 10 seconds after container start, then reload Nginx
docker restart rapiddocs && sleep 10 && sudo systemctl reload nginx

# Or: Fix Nginx proxy settings
sudo nano /etc/nginx/sites-available/rapiddocs.io
# Ensure proxy_pass points to: http://localhost:8000
```

### Issue 5: DNS Not Resolving

**Symptom**: `dig rapiddocs.io` doesn't return your VPS IP

**Fix**:
```bash
# Check current DNS
dig rapiddocs.io +short

# If it doesn't show your VPS IP:
# 1. Go to your domain registrar
# 2. Update A records to point to your VPS IP
# 3. Wait 5-30 minutes for propagation

# Get your VPS IP
curl ifconfig.me
```

### Issue 6: SSL Certificate Issues

**Symptom**: HTTPS doesn't work or shows certificate error

**Fix**:
```bash
# Check certificate status
sudo certbot certificates

# Renew if needed
sudo certbot renew --force-renewal

# Reload Nginx after certificate changes
sudo systemctl reload nginx
```

## Step-by-Step Debugging Process

Run these commands in order and note where it fails:

```bash
# 1. Check container is running
docker ps | grep rapiddocs
# ✅ Expected: Shows rapiddocs container running

# 2. Check container logs
docker logs rapiddocs | tail -20
# ✅ Expected: "Application startup complete"

# 3. Test health endpoint inside VPS
curl http://localhost:8000/health
# ✅ Expected: {"status":"healthy"}

# 4. Test from Nginx
curl -H "Host: rapiddocs.io" http://localhost
# ✅ Expected: HTML content

# 5. Check Nginx error logs
sudo tail -20 /var/log/nginx/error.log
# ✅ Expected: No recent errors

# 6. Check DNS
dig rapiddocs.io +short
# ✅ Expected: Your VPS IP

# 7. Test from outside (if you have another machine)
curl -I https://rapiddocs.io
# ✅ Expected: HTTP 200 OK
```

## Full Restart Procedure

If all else fails, restart everything:

```bash
# 1. Stop container
docker stop rapiddocs
docker rm rapiddocs

# 2. Rebuild and run
cd ~/rapiddocs
docker build -t rapiddocs:latest .
docker run -d \
  --name rapiddocs \
  --restart unless-stopped \
  -p 8000:8000 \
  -v ~/rapiddocs/backend/uploads:/app/uploads \
  -v ~/rapiddocs/backend/generated_pdfs:/app/generated_pdfs \
  --env-file ~/rapiddocs/backend/.env \
  rapiddocs:latest

# 3. Wait for startup
sleep 10

# 4. Check logs
docker logs rapiddocs

# 5. Test health
curl http://localhost:8000/health

# 6. Restart Nginx
sudo systemctl restart nginx

# 7. Check Nginx status
sudo systemctl status nginx

# 8. Test site
curl -I https://rapiddocs.io
```

## Get Complete Diagnostic Information

Run this command to get all diagnostic info:

```bash
# Create diagnostic report
cat > ~/diagnostic.sh << 'EOF'
#!/bin/bash
echo "=== Docker Container Status ==="
docker ps | grep rapiddocs

echo -e "\n=== Container Logs (last 50 lines) ==="
docker logs --tail 50 rapiddocs

echo -e "\n=== Test Health Endpoint ==="
curl http://localhost:8000/health

echo -e "\n=== Nginx Status ==="
sudo systemctl status nginx | head -20

echo -e "\n=== Nginx Error Logs (last 20 lines) ==="
sudo tail -20 /var/log/nginx/error.log

echo -e "\n=== DNS Resolution ==="
dig rapiddocs.io +short

echo -e "\n=== Firewall Status ==="
sudo ufw status

echo -e "\n=== Listening Ports ==="
sudo netstat -tlnp | grep -E ':(80|443|8000)'

echo -e "\n=== Environment File Exists ==="
ls -la ~/rapiddocs/backend/.env

echo -e "\n=== VPS IP Address ==="
curl -s ifconfig.me
EOF

chmod +x ~/diagnostic.sh
./diagnostic.sh
```

Copy the output and we can identify the exact issue!

## Most Likely Issue Based on Your Output

Looking at your deployment, the most likely issues are:

1. **Container logs were cut off** - We need to see full logs to check if MongoDB connected
2. **DNS not propagated yet** - If you just updated DNS, wait 30 minutes
3. **MongoDB IP not whitelisted** - Your VPS IP needs to be in MongoDB Atlas

Run this to quickly check:

```bash
# Quick check
echo "Container logs:"
docker logs rapiddocs 2>&1 | grep -E "(ERROR|WARNING|Application startup|Connected to MongoDB)"

echo -e "\nHealth check:"
curl http://localhost:8000/health

echo -e "\nDNS:"
dig rapiddocs.io +short

echo -e "\nVPS IP:"
curl -s ifconfig.me
```

Send me the output and I'll tell you exactly what's wrong!
