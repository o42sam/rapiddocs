# Production Deployment Guide - Bitcoin Payment System

## Quick Start for Production

### 1. Environment Configuration

Create a `.env.production` file:

```bash
# Application
APP_NAME=RapidDocs
APP_ENV=production
DEBUG=False
API_PREFIX=/api/v1

# MongoDB
MONGODB_URL=mongodb+srv://YOUR_USER:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/
MONGODB_DB_NAME=rapiddocs_production

# Hugging Face
HUGGINGFACE_API_KEY=YOUR_PRODUCTION_KEY
TEXT_GENERATION_MODEL=meta-llama/Llama-3.2-3B-Instruct
IMAGE_GENERATION_MODEL=black-forest-labs/FLUX.1-schnell

# Bitcoin - MAINNET CONFIGURATION
BITCOIN_NETWORK=mainnet
BITCOIN_PERSONAL_WALLET=YOUR_MAINNET_BITCOIN_ADDRESS
BITCOIN_CONFIRMATIONS_REQUIRED=6
BITCOIN_PAYMENT_TIMEOUT_MINUTES=120
BITCOIN_API_URL=https://blockstream.info/api

# Security - CRITICAL: Generate new keys!
JWT_SECRET_KEY=GENERATE_STRONG_RANDOM_KEY_HERE
JWT_REFRESH_SECRET_KEY=GENERATE_DIFFERENT_STRONG_KEY_HERE
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS - Update with your production domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. Generate Secure Keys

```bash
# Generate JWT secret keys
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
# Use output for JWT_SECRET_KEY

python3 -c "import secrets; print(secrets.token_urlsafe(64))"
# Use output for JWT_REFRESH_SECRET_KEY
```

### 3. Set Up Personal Bitcoin Wallet

**⚠️ IMPORTANT: Never use a temporary or payment address as your personal wallet!**

1. Create a secure Bitcoin wallet (hardware wallet recommended)
2. Generate a mainnet receiving address
3. Add it to `BITCOIN_PERSONAL_WALLET` in `.env.production`
4. Backup wallet recovery phrase securely

### 4. Deploy Backend

#### Option A: Docker Deployment (Recommended)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app ./app
COPY .env.production .env

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t rapiddocs-backend .
docker run -d -p 8000:8000 --env-file .env.production rapiddocs-backend
```

#### Option B: Traditional Server Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Copy production environment
cp .env.production .env

# Run with Gunicorn (production WSGI server)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 5. Set Up HTTPS

```nginx
# nginx configuration
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6. Monitoring Setup

```bash
# Install monitoring tools
pip install sentry-sdk

# Add to app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FastApiIntegration()],
    environment="production"
)
```

### 7. Database Backups

```bash
# MongoDB Atlas: Enable automatic backups
# Or use mongodump for manual backups
mongodump --uri="YOUR_MONGODB_URL" --out=/backup/$(date +%Y%m%d)
```

### 8. Testing on Testnet First

**BEFORE mainnet deployment:**

```bash
# Test with testnet configuration
BITCOIN_NETWORK=testnet
BITCOIN_API_URL=https://blockstream.info/testnet/api

# Process 20-50 real testnet payments
# Monitor for issues
# Fix any bugs found
```

## Maintenance Procedures

### Daily Tasks

```bash
# Check payment logs
tail -f /var/log/rapiddocs/payments.log

# Verify forwarding transactions
curl https://blockstream.info/api/address/YOUR_WALLET/txs

# Monitor error rates
# Use your monitoring dashboard (Sentry, Datadog, etc.)
```

### Weekly Tasks

```bash
# Database reconciliation
python scripts/reconcile_payments.py

# Review expired payments
python scripts/check_expired_payments.py

# Update Bitcoin price cache
# Handled automatically by the system
```

### Monthly Tasks

```bash
# Review transaction fees
# Adjust confirmation requirements if needed
# Update pricing based on BTC volatility
# Review security logs
# Check for system updates
```

## Emergency Procedures

### Payment Not Forwarding

```python
# Manual forwarding script
from app.services.bitcoin_forwarder import bitcoin_forwarder_service
from app.routes.bitcoin import decrypt_private_key

# Get payment from database
payment = db.bitcoin_payments.find_one({"_id": ObjectId("PAYMENT_ID")})

# Decrypt private key
private_key = decrypt_private_key(payment["private_key_encrypted"])

# Forward manually
result = bitcoin_forwarder_service.forward_funds(
    private_key,
    payment["payment_address"]
)

print(f"Forwarding result: {result}")
```

### System Recovery

```bash
# Restart backend
systemctl restart rapiddocs-backend

# Check database connection
python -c "from app.database import get_database; print('DB Connected')"

# Verify Bitcoin API connectivity
curl https://blockstream.info/api/blocks/tip/height
```

## Security Best Practices

1. **Never commit .env files to Git**
2. **Use environment variables for all secrets**
3. **Rotate JWT keys every 90 days**
4. **Monitor for suspicious payment patterns**
5. **Keep Bitcoin wallet offline when not forwarding**
6. **Use hardware wallet for personal Bitcoin wallet**
7. **Enable 2FA for all admin accounts**
8. **Regular security audits**
9. **Keep all dependencies updated**
10. **Implement rate limiting**

## Rollback Procedure

If issues arise in production:

```bash
# 1. Stop new payments
# Update environment to maintenance mode

# 2. Process pending payments
python scripts/process_pending_payments.py

# 3. Rollback to previous version
git checkout PREVIOUS_VERSION_TAG
docker-compose down && docker-compose up -d

# 4. Verify system health
curl https://api.yourdomain.com/health

# 5. Monitor logs
tail -f /var/log/rapiddocs/*.log
```

## Cost Optimization

### Reduce API Calls

```python
# Implement caching for BTC/USD rate
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=1)
def get_cached_btc_rate():
    cache_time = datetime.utcnow()
    rate = bitcoin_monitor_service.get_btc_to_usd_rate()
    return rate, cache_time

# Use cached rate if less than 5 minutes old
```

### Optimize Blockchain Queries

```python
# Batch payment status checks
# Check multiple payments in single API call
```

## Compliance & Legal

- **KYC/AML:** Consider implementing if required in your jurisdiction
- **Tax Reporting:** Maintain detailed transaction logs
- **Privacy Policy:** Update to include Bitcoin payment processing
- **Terms of Service:** Add cryptocurrency payment terms
- **Refund Policy:** Define Bitcoin refund procedures

## Support Escalation

### Level 1: User Can't Send Payment
- Verify payment address
- Check Bitcoin wallet status
- Confirm amount is correct

### Level 2: Payment Not Detected
- Check blockchain explorer
- Verify transaction ID
- Wait for confirmations

### Level 3: Forwarding Failed
- Check personal wallet address
- Verify sufficient balance for fees
- Manual forwarding may be required

## Performance Tuning

### Database Indexing

```javascript
// MongoDB indexes
db.bitcoin_payments.createIndex({ "user_id": 1 })
db.bitcoin_payments.createIndex({ "payment_address": 1 })
db.bitcoin_payments.createIndex({ "status": 1 })
db.bitcoin_payments.createIndex({ "created_at": -1 })
db.bitcoin_payments.createIndex({ "expires_at": 1 })
```

### API Response Caching

```python
# Cache package data
@lru_cache(maxsize=1)
def get_packages():
    return CREDITS_PACKAGES
```

## Success Metrics

Track these KPIs:

- Payment success rate
- Average time to confirmation
- Forwarding success rate
- User satisfaction (CSAT)
- Revenue per payment method
- Abandoned payments rate

## Conclusion

Follow this guide carefully to ensure a smooth production deployment. Always test thoroughly on testnet before moving to mainnet with real Bitcoin.

**Questions or Issues?**
- Review logs: `/var/log/rapiddocs/`
- Check monitoring dashboard
- Consult blockchain explorer
- Contact development team

---

**Last Updated:** 2025-11-10
**Version:** 1.0.0
