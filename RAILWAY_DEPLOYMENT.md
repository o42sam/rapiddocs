# Railway Deployment Guide

This guide walks you through deploying the Document Generator application to Railway.

## Why Railway?

Railway has excellent MongoDB Atlas support and handles TLS/SSL connections properly, unlike some other platforms. Your application will work with MongoDB Atlas without any modifications.

## Prerequisites

1. Railway account (sign up at https://railway.app)
2. GitHub repository with your code
3. MongoDB Atlas cluster with connection string

## Deployment Steps

### 1. Connect GitHub Repository

1. Go to https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Authorize Railway to access your GitHub account
4. Select repository: `o42sam/rapiddocs`
5. Railway will automatically detect your Dockerfile

### 2. Configure Environment Variables

After creating the project, go to your service settings and add these environment variables:

**Required Variables:**

```bash
# Application
APP_ENV=production
DEBUG=False

# MongoDB Atlas
MONGODB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DB_NAME=docgen

# Hugging Face
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxx
TEXT_GENERATION_MODEL=mistralai/Mistral-7B-Instruct-v0.2
IMAGE_GENERATION_MODEL=black-forest-labs/FLUX.1-schnell

# PDF Generation
PDF_DPI=300

# CORS (Railway provides domain automatically)
CORS_ORIGINS=https://your-app.up.railway.app

# Port (Railway sets this automatically)
PORT=8000
```

**Optional Variables:**

```bash
RATE_LIMIT_PER_MINUTE=10
MAX_UPLOAD_SIZE=5242880
ALLOWED_IMAGE_FORMATS=png,jpg,jpeg,svg
```

### 3. Get Your MongoDB Connection String

1. Go to MongoDB Atlas: https://cloud.mongodb.com
2. Click **"Connect"** on your cluster
3. Choose **"Connect your application"**
4. Select **Driver: Python**, **Version: 3.12 or later**
5. Copy the connection string
6. Replace `<username>` and `<password>` with your database credentials
7. Paste the full string into Railway's `MONGODB_URL` variable

Example:
```
mongodb+srv://myuser:mypassword@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

### 4. Deploy

Railway will automatically:
1. Build your Docker image using the Dockerfile
2. Deploy the container
3. Assign a public URL (e.g., `https://rapiddocs-production.up.railway.app`)

**Build Process** (what Railway does):
- Runs multi-stage Docker build
- Stage 1: Builds frontend with Node.js
- Stage 2: Sets up Python backend and copies frontend build
- Exposes port 8000
- Starts uvicorn server

### 5. Update CORS Origins

After deployment:
1. Note your Railway app URL (e.g., `https://rapiddocs-production.up.railway.app`)
2. Update the `CORS_ORIGINS` environment variable to include this URL
3. Railway will automatically redeploy

Example:
```bash
CORS_ORIGINS=https://rapiddocs-production.up.railway.app
```

### 6. Verify Deployment

1. **Check Logs**:
   - Go to your Railway project
   - Click on the service
   - View **"Deployments"** tab
   - Check logs for successful MongoDB connection:
     ```
     ✓ Connected to MongoDB: docgen
     ✓ Available collections: [...]
     ```

2. **Test the Application**:
   - Visit your Railway URL
   - Try generating a document
   - Check that MongoDB is connected (should see data persistence)

## Railway CLI (Optional)

You can also deploy using Railway CLI:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# Deploy
railway up

# View logs
railway logs

# Set environment variables
railway variables set MONGODB_URL="mongodb+srv://..."
```

## Troubleshooting

### MongoDB Connection Issues

If you see MongoDB errors:

1. **Check MongoDB Atlas Network Access**:
   - Go to Atlas → Network Access
   - Add IP: `0.0.0.0/0` (allow all) for Railway
   - Railway uses dynamic IPs, so you need to allow all

2. **Verify Connection String**:
   - Ensure no spaces or line breaks
   - Check username/password are correct
   - Verify cluster name matches

3. **Check Logs**:
   ```bash
   railway logs
   ```
   Look for MongoDB connection messages

### Build Failures

If Docker build fails:

1. Check Dockerfile exists in repository root
2. Verify frontend/backend directories are present
3. Check Railway build logs for specific errors

### Application Not Loading

1. **Check Port Configuration**:
   - Railway automatically sets `PORT` environment variable
   - Our Dockerfile exposes port 8000
   - Backend should listen on `0.0.0.0:8000`

2. **Check Static Files**:
   - Frontend build should be in `backend/static/`
   - Verify multi-stage build completed successfully

### CORS Errors

1. Update `CORS_ORIGINS` to include your Railway domain
2. Redeploy after changing environment variables

## Monitoring

Railway provides:
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: History of all deployments
- **Analytics**: Request metrics

Access these from your Railway project dashboard.

## Scaling

Railway offers:
- **Horizontal Scaling**: Multiple instances (Pro plan)
- **Vertical Scaling**: Increase CPU/memory
- **Auto-scaling**: Based on load (Pro plan)

## Cost

- **Hobby Plan**: $5/month for 500 hours of usage
- **Pro Plan**: Pay-as-you-go for resources used

Your app should fit comfortably in the Hobby plan for development/testing.

## Custom Domain (Optional)

1. Go to your Railway service settings
2. Click **"Networking"**
3. Add your custom domain
4. Update DNS records as instructed
5. Railway provides automatic HTTPS with Let's Encrypt

## Environment-Specific Configuration

Railway automatically sets:
- `RAILWAY_ENVIRONMENT` (production/staging)
- `RAILWAY_SERVICE_NAME`
- `RAILWAY_DEPLOYMENT_ID`

You can use these for conditional logic if needed.

## Continuous Deployment

Railway automatically deploys when you push to your GitHub repository:

```bash
git add .
git commit -m "Update feature"
git push origin master
```

Railway will:
1. Detect the push
2. Trigger a new build
3. Deploy automatically
4. Zero-downtime deployment

## Health Checks

Railway automatically monitors your application health. To add custom health check:

```python
# In backend/app/main.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mongodb": db.connected,
        "timestamp": datetime.now().isoformat()
    }
```

## Database Backups

Railway doesn't backup your MongoDB Atlas data. Configure backups in MongoDB Atlas:

1. Atlas → Backup
2. Enable continuous backups
3. Configure backup schedule

## Support

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- MongoDB Atlas Support: https://www.mongodb.com/support

## Next Steps

After successful deployment:

1. Test all features (document generation, logo upload, statistics)
2. Monitor logs for any errors
3. Set up MongoDB Atlas backups
4. Configure custom domain (optional)
5. Set up monitoring alerts (optional)

---

Your application should now be running successfully on Railway with full MongoDB Atlas connectivity!
