# Deployment Guide for Sevalla (or any Docker-based platform)

This guide will help you deploy the Document Generator application to Sevalla or any other Docker-based hosting platform.

## Prerequisites

Before deploying, ensure you have:

1. **MongoDB Atlas Account** with a cluster set up
2. **HuggingFace Account** with an API token
3. **Git Repository** with your code pushed
4. **Sevalla Account** (or alternative Docker hosting)

## Step 1: Set Up MongoDB Atlas

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster (free tier works fine)
3. Create a database user:
   - Click "Database Access" → "Add New Database User"
   - Set username and password
   - Grant "Read and write to any database" role
4. Whitelist all IP addresses:
   - Click "Network Access" → "Add IP Address"
   - Click "Allow Access from Anywhere" (0.0.0.0/0)
5. Get your connection string:
   - Click "Database" → "Connect" → "Connect your application"
   - Copy the connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

## Step 2: Get HuggingFace API Token

1. Go to [HuggingFace](https://huggingface.co/)
2. Sign up or log in
3. Go to Settings → Access Tokens
4. Click "New token"
5. Give it a name (e.g., "docgen-production")
6. Set role to "Read"
7. Copy the token (starts with `hf_`)

## Step 3: Configure Environment Variables

In your Sevalla dashboard (or hosting platform):

1. Navigate to your app's environment variables section
2. Add the following variables:

```
# Application
APP_NAME=DocGenerator
APP_ENV=production
DEBUG=False
API_PREFIX=/api/v1

# MongoDB Atlas
MONGODB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/
MONGODB_DB_NAME=docgen

# HuggingFace
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxx
TEXT_GENERATION_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# File Storage
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=5242880
ALLOWED_IMAGE_FORMATS=png,jpg,jpeg,svg

# PDF Generation
PDF_OUTPUT_DIR=./generated_pdfs
PDF_DPI=300

# API Rate Limiting
RATE_LIMIT_PER_MINUTE=10

# CORS (Update with your actual domain)
CORS_ORIGINS=https://yourdomain.sevalla.app,https://www.yourdomain.com
```

**Important**: Replace `<username>`, `<password>`, `<cluster>`, and the HuggingFace token with your actual values.

## Step 4: Deploy to Sevalla

### Option A: Using Sevalla Dashboard

1. Log in to [Sevalla](https://sevalla.com/)
2. Click "Create New App"
3. Select "Deploy from GitHub"
4. Authorize Sevalla to access your repository
5. Select your `rapiddocs` repository
6. Configure build settings:
   - **Build Method**: Dockerfile
   - **Dockerfile Path**: `Dockerfile` (in root)
   - **Port**: 8000
7. Add environment variables (from Step 3)
8. Click "Deploy"

### Option B: Using Sevalla CLI (if available)

```bash
# Install Sevalla CLI
npm install -g @sevalla/cli

# Login
sevalla login

# Deploy
sevalla deploy
```

## Step 5: Verify Deployment

1. Wait for the build to complete (5-10 minutes)
2. Once deployed, visit your app URL (e.g., `https://yourapp.sevalla.app`)
3. You should see the document generator interface
4. Test the health endpoint: `https://yourapp.sevalla.app/health`
5. Check API docs: `https://yourapp.sevalla.app/api/v1/docs`

## Troubleshooting

### Build Fails with "Nixpacks unable to generate build plan"

**Solution**: Make sure you have the `Dockerfile` in the root directory of your repository. Sevalla should automatically detect it.

### MongoDB Connection Fails

**Symptoms**: Logs show "MongoDB connection failed"

**Solutions**:
1. Verify your MongoDB connection string is correct
2. Ensure you've whitelisted all IPs (0.0.0.0/0) in MongoDB Atlas
3. Check that your database username and password are correct
4. Make sure you're using the correct connection string format

### Text Generation Fails

**Symptoms**: Document generation fails during text generation step

**Solutions**:
1. Verify your HuggingFace API token is valid
2. Check that you have access to the model (some models require approval)
3. Try using a different model: `meta-llama/Llama-2-7b-chat-hf` or `google/flan-t5-large`
4. Check HuggingFace API status

### Frontend Can't Connect to Backend

**Symptoms**: API calls fail with CORS errors or 404s

**Solutions**:
1. Check that `CORS_ORIGINS` includes your actual domain
2. Verify the frontend is being served correctly (visit your domain)
3. Check browser console for specific errors

### Out of Memory Errors

**Symptoms**: Container crashes or restarts frequently

**Solutions**:
1. Upgrade to a plan with more memory
2. Reduce `max_new_tokens` in text generation
3. Use a smaller model for text generation

## Environment-Specific Notes

### Production vs Development

The application automatically detects the environment:

- **Production** (HuggingFace API key present): Uses HuggingFace API for text generation
- **Development** (No HuggingFace key): Uses local Ollama (requires Ollama to be running)

### File Storage

Currently, files are stored in the container's filesystem. For production:

- Files will be lost on container restart
- Consider adding AWS S3 or similar cloud storage for persistence
- Add volume mounts if your platform supports it

## Monitoring

### Health Check

The application provides a health endpoint:

```
GET /health
Response: {"status": "healthy"}
```

Configure your platform to monitor this endpoint.

### Logs

View application logs in your Sevalla dashboard:

1. Navigate to your app
2. Click "Logs"
3. Filter by time range or search for specific errors

## Scaling Considerations

For high traffic, consider:

1. **Horizontal Scaling**: Run multiple instances
2. **Database**: Upgrade MongoDB Atlas tier
3. **CDN**: Use CloudFlare or similar for static assets
4. **Caching**: Add Redis for caching generated documents
5. **Queue**: Add Celery/RabbitMQ for background processing

## Security Recommendations

1. **API Keys**: Never commit API keys to Git
2. **CORS**: Restrict to your actual domain (not `*`)
3. **Rate Limiting**: Implemented by default, adjust as needed
4. **File Upload**: Already limited to 5MB, validate file types
5. **HTTPS**: Sevalla provides this automatically

## Alternative Deployment Platforms

This Dockerfile works with:

- **Railway**: railway.app
- **Render**: render.com
- **Fly.io**: fly.io
- **Google Cloud Run**: cloud.google.com/run
- **AWS ECS/Fargate**: aws.amazon.com/ecs
- **DigitalOcean App Platform**: digitalocean.com/products/app-platform
- **Heroku**: heroku.com (with buildpack)

## Cost Estimates

### Free Tier
- **MongoDB Atlas**: Free (512MB storage)
- **HuggingFace API**: Free tier available (rate limited)
- **Sevalla**: Check their pricing

### Paid Tier (Recommended for production)
- **MongoDB Atlas**: $9-25/month (shared tier)
- **HuggingFace Pro**: $9/month (higher rate limits)
- **Sevalla/Hosting**: Varies by platform ($5-20/month)

## Support

For issues:
1. Check application logs
2. Review this deployment guide
3. Check platform-specific documentation
4. Create an issue in the GitHub repository

## Next Steps

After successful deployment:

1. Test document generation with various inputs
2. Monitor error rates and response times
3. Set up automated backups for MongoDB
4. Consider adding authentication for production use
5. Implement document storage in cloud (S3/CloudFlare R2)
