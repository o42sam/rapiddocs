# RapidDocs Production Setup Guide

This guide provides instructions for deploying RapidDocs to production at rapiddocs.io.

## Prerequisites

- Domain: `rapiddocs.io` configured with DNS
- MongoDB Atlas cluster
- Hugging Face API key
- Production server (Railway, Vercel, AWS, etc.)

## Backend Deployment

### 1. Environment Configuration

Create a `.env` file in the `backend/` directory based on `.env.production.example`:

```bash
cd backend
cp .env.production.example .env
```

### 2. Update Environment Variables

Edit `.env` and set the following:

```bash
# Application
APP_NAME=RapidDocs
APP_ENV=production
DEBUG=False
API_PREFIX=/api/v1

# MongoDB Atlas - REQUIRED
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?appName=rapiddocs
MONGODB_DB_NAME=rapiddocs_prod

# Hugging Face - REQUIRED
HUGGINGFACE_API_KEY=hf_your_actual_api_key_here

# CORS - Include your production domain
CORS_ORIGINS=https://rapiddocs.io,https://www.rapiddocs.io

# Authentication - CRITICAL: Generate strong keys
# Generate with: openssl rand -hex 32
JWT_SECRET_KEY=your_generated_secret_key_here
JWT_REFRESH_SECRET_KEY=your_other_generated_secret_key_here
```

### 3. Generate Secret Keys

```bash
# Generate JWT secret keys
openssl rand -hex 32  # Use for JWT_SECRET_KEY
openssl rand -hex 32  # Use for JWT_REFRESH_SECRET_KEY
```

### 4. Deploy Backend

#### Option A: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Deploy
railway up
```

#### Option B: Docker

```bash
cd backend
docker build -t rapiddocs-backend .
docker run -p 8000:8000 --env-file .env rapiddocs-backend
```

### 5. Verify Backend Deployment

Visit: `https://your-backend-url.com/api/v1/docs`

You should see the FastAPI Swagger documentation.

## Frontend Deployment

### 1. Environment Configuration

The frontend uses `.env.production` for production builds:

```bash
# Already created at frontend/.env.production
VITE_API_BASE_URL=https://rapiddocs.io/api/v1
VITE_MAX_FILE_SIZE=5242880
VITE_SUPPORTED_FORMATS=image/png,image/jpeg,image/svg+xml
```

**Important**: If your backend is on a different domain (e.g., `api.rapiddocs.io`), update `VITE_API_BASE_URL` accordingly.

### 2. Build Frontend

```bash
cd frontend
npm install
npm run build
```

This creates optimized production files in `frontend/dist/`

### 3. Deploy Frontend

#### Option A: Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod
```

Configure custom domain in Vercel dashboard: `rapiddocs.io`

#### Option B: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd frontend
netlify deploy --prod --dir=dist
```

Configure custom domain in Netlify dashboard: `rapiddocs.io`

#### Option C: Static Hosting (Nginx, Apache, etc.)

Upload contents of `frontend/dist/` to your web server.

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name rapiddocs.io www.rapiddocs.io;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name rapiddocs.io www.rapiddocs.io;

    # SSL certificates
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    root /var/www/rapiddocs/dist;
    index index.html;

    # Frontend - Single Page Application
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Database Setup

### MongoDB Atlas

1. **Create a Production Cluster**
   - Go to [MongoDB Atlas](https://cloud.mongodb.com)
   - Create a new cluster or use existing one
   - Database name: `rapiddocs_prod`

2. **Create Database User**
   - Go to Database Access
   - Add new database user with username and password
   - Save credentials securely

3. **Configure Network Access**
   - Go to Network Access
   - Add IP addresses that will connect to the database
   - For cloud deployments, add the service's IP range
   - Or use `0.0.0.0/0` (less secure, but works for dynamic IPs)

4. **Get Connection String**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your actual password
   - Add to backend `.env` as `MONGODB_URL`

## SSL/HTTPS Setup

### Option A: Let's Encrypt (Free)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d rapiddocs.io -d www.rapiddocs.io

# Auto-renewal
sudo certbot renew --dry-run
```

### Option B: Cloudflare (Free)

1. Add domain to Cloudflare
2. Update nameservers at your domain registrar
3. Enable "Full (strict)" SSL mode
4. Cloudflare will automatically provide SSL

## Post-Deployment Checklist

- [ ] Backend is accessible at `https://rapiddocs.io/api/v1/docs`
- [ ] Frontend loads at `https://rapiddocs.io`
- [ ] User registration works
- [ ] User login works
- [ ] Document generation works (with authentication)
- [ ] Logo upload works
- [ ] Form data persistence works
- [ ] MongoDB connection is secure
- [ ] CORS is properly configured
- [ ] JWT secret keys are strong and unique
- [ ] SSL certificate is valid
- [ ] Environment variables are set (not using defaults)
- [ ] Debug mode is OFF (`DEBUG=False`)
- [ ] API rate limiting is active
- [ ] Error logging is configured
- [ ] Backups are scheduled (MongoDB)

## Monitoring

### Backend Health Check

```bash
curl https://rapiddocs.io/api/v1/health
```

### Database Connection Test

Check backend logs for MongoDB connection confirmation.

### Error Tracking

Consider integrating:
- Sentry for error tracking
- LogRocket for session replay
- Google Analytics for usage metrics

## Troubleshooting

### "Failed to load resource: net::ERR_CONNECTION_REFUSED"

**Cause**: Frontend can't reach backend API

**Solutions**:
1. Verify `VITE_API_BASE_URL` in `.env.production`
2. Check backend is running and accessible
3. Verify CORS settings in backend
4. Check firewall rules

### "CORS policy: No 'Access-Control-Allow-Origin' header"

**Cause**: Backend CORS not configured for frontend domain

**Solution**: Add `https://rapiddocs.io` to `CORS_ORIGINS` in backend `.env`

### "401 Unauthorized" on API calls

**Cause**: JWT token issues

**Solutions**:
1. Check JWT secret keys match between requests
2. Verify tokens are being sent in Authorization header
3. Check token expiration settings

### MongoDB Connection Failed

**Cause**: Database credentials or network access issue

**Solutions**:
1. Verify `MONGODB_URL` is correct
2. Check database user has proper permissions
3. Verify IP whitelist in MongoDB Atlas
4. Check network connectivity

## Security Best Practices

1. **Never commit `.env` files** - Already in `.gitignore`
2. **Use strong JWT secret keys** - Generate with `openssl rand -hex 32`
3. **Enable HTTPS only** - Redirect HTTP to HTTPS
4. **Limit CORS origins** - Only allow your domain
5. **Set secure MongoDB password** - Use strong, unique password
6. **Enable MongoDB Atlas encryption** - At rest and in transit
7. **Regular security updates** - Keep dependencies updated
8. **Rate limiting** - Prevent abuse
9. **Input validation** - Already implemented in backend
10. **Regular backups** - MongoDB Atlas automated backups

## Maintenance

### Update Application

```bash
# Pull latest changes
git pull origin master

# Backend
cd backend
pip install -r requirements.txt
# Restart backend service

# Frontend
cd frontend
npm install
npm run build
# Deploy new build
```

### Monitor Logs

```bash
# Backend logs
tail -f /var/log/rapiddocs/backend.log

# Or if using Railway/Vercel
railway logs  # or vercel logs
```

## Support

For issues or questions:
- GitHub Issues: [Repository Issues](https://github.com/o42sam/rapiddocs/issues)
- Email: samscarfaceegbo@gmail.com

## License

[Your License Here]
