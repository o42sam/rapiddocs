FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf-2.0-dev \
    libffi-dev \
    shared-mime-info \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi==0.109.0 \
    uvicorn[standard]==0.27.0 \
    gunicorn==21.2.0 \
    pydantic==2.5.3 \
    pydantic-settings==2.1.0 \
    python-dotenv==1.0.0 \
    python-multipart==0.0.6 \
    motor==3.3.2 \
    pymongo[srv]==4.6.1 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    bcrypt==4.1.2 \
    cryptography==41.0.7 \
    email-validator==2.1.0 \
    authlib==1.3.0 \
    google-generativeai==0.3.2 \
    huggingface-hub==0.20.2 \
    httpx==0.26.0 \
    reportlab==4.0.8 \
    Pillow==10.2.0 \
    PyPDF2==3.0.1 \
    cairosvg==2.7.1 \
    matplotlib==3.8.2 \
    numpy==1.26.3 \
    aiofiles==23.2.1 \
    jinja2==3.1.3 \
    python-multipart==0.0.6

# Copy application code
COPY app /app/app
COPY .env.production /app/.env

# Create necessary directories
RUN mkdir -p /app/uploads/logos /app/generated_pdfs/invoices /app/logs

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main_simple:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]