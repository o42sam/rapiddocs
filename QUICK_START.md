# RapidDocs Hostinger VPS - Quick Start Checklist

## Pre-Deployment (5 minutes)

- [ ] Purchase Hostinger VPS ($3.99/month)
  - Go to: https://www.hostinger.com/vps-hosting
  - Select KVM 1 plan
  - **Pay with Bitcoin/Crypto** via CoinGate
  - Wait for VPS credentials email

- [ ] Prepare MongoDB Atlas IP Whitelist
  - Log into MongoDB Atlas
  - Go to: Network Access → IP Access List
  - Have "Add IP Address" ready (you'll add VPS IP after purchase)

---

## Initial Setup (10 minutes)

```bash
# 1. Connect to VPS
ssh root@YOUR_VPS_IP

# 2. Quick system update
apt update && apt upgrade -y && apt install -y curl git ufw

# 3. Configure firewall
ufw allow 22 && ufw allow 80 && ufw allow 443 && ufw --force enable

# 4. Install Docker
curl -fsSL https://get.docker.com | sh && usermod -aG docker root

# 5. Install Nginx and Certbot
apt install -y nginx certbot python3-certbot-nginx
```

---

## Deploy Application (10 minutes)

```bash
# 1. Clone repository
cd ~ && git clone https://github.com/o42sam/rapiddocs.git && cd rapiddocs

# 2. Configure environment
cd backend && nano .env
# Copy your production environment variables
# Save: Ctrl+X → Y → Enter

# 3. Add VPS IP to MongoDB Atlas
# In Atlas: Network Access → Add IP Address → Add YOUR_VPS_IP

# 4. Build and run Docker
cd ~/rapiddocs
docker build -t rapiddocs:latest .
docker run -d --name rapiddocs --restart unless-stopped -p 8000:8000 \
  -v ~/rapiddocs/backend/uploads:/app/uploads \
  -v ~/rapiddocs/backend/generated_pdfs:/app/generated_pdfs \
  --env-file ~/rapiddocs/backend/.env rapiddocs:latest

# 5. Test application
docker logs rapiddocs
curl http://localhost:8000/health
```

---

## Configure Domain (15 minutes)

```bash
# 1. Set up Nginx
cat > /etc/nginx/sites-available/rapiddocs.io << 'EOF'
server {
    listen 80;
    server_name rapiddocs.io www.rapiddocs.io;
    client_max_body_size 10M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
    }
}
EOF

# 2. Enable site
ln -s /etc/nginx/sites-available/rapiddocs.io /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 3. Update DNS (on your domain registrar)
# Add A records:
# @ → YOUR_VPS_IP
# www → YOUR_VPS_IP

# 4. Wait for DNS propagation (5-30 minutes)
# Check: dig rapiddocs.io

# 5. Get SSL certificate
certbot --nginx -d rapiddocs.io -d www.rapiddocs.io
# Enter email, agree to terms, choose redirect (yes)
```

---

## Verification (2 minutes)

```bash
# Test everything
curl -I https://rapiddocs.io/health                    # Should return 200
curl https://rapiddocs.io/api/v1/docs                  # Should load API docs
docker logs rapiddocs | grep "Application startup"     # Should show "complete"
systemctl status nginx                                  # Should be "active (running)"
```

---

## Done! 🎉

Your application is now live at: **https://rapiddocs.io**

### What You Have:

✅ FastAPI application running in Docker
✅ MongoDB Atlas connected
✅ Nginx reverse proxy configured
✅ SSL certificate (HTTPS) enabled
✅ Automatic container restart on reboot
✅ Firewall configured
✅ Domain configured with SSL

### Total Time: ~40 minutes
### Total Cost: $3.99/month (paid with crypto)

---

## Quick Commands

```bash
# View logs
docker logs -f rapiddocs

# Restart app
docker restart rapiddocs

# Update app
cd ~/rapiddocs && git pull && docker build -t rapiddocs:latest . && \
docker stop rapiddocs && docker rm rapiddocs && \
docker run -d --name rapiddocs --restart unless-stopped -p 8000:8000 \
  -v ~/rapiddocs/backend/uploads:/app/uploads \
  -v ~/rapiddocs/backend/generated_pdfs:/app/generated_pdfs \
  --env-file ~/rapiddocs/backend/.env rapiddocs:latest

# Check resources
docker stats rapiddocs

# Access container shell
docker exec -it rapiddocs bash
```

---

## Troubleshooting

**Container not starting?**
```bash
docker logs rapiddocs  # Check error messages
```

**Can't connect to MongoDB?**
- Check MongoDB Atlas → Network Access
- Ensure VPS IP is whitelisted

**Site not loading?**
```bash
systemctl status nginx  # Check Nginx status
docker ps               # Check container running
```

**Need more help?**
See full guide: `HOSTINGER_DEPLOY.md`
