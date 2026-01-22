# RapidDocs - AI-Powered Document Generation Platform

Professional document generation platform that creates invoices, infographic documents, and formal documents using AI technology.

## 🚀 Features

### Document Types
1. **Invoices** - Professional business invoices with AI-generated content
2. **Infographic Documents** - Visual documents with charts and AI-generated images
3. **Formal Documents** - Professional text documents with watermarks and formatting

### Core Capabilities
- ✨ AI-powered text generation (Google Gemini)
- 🎨 AI-powered image generation (HuggingFace)
- 📊 Data visualization with charts and graphs
- 📄 Multiple output formats (PDF, DOCX, HTML)
- 💾 CSV/Excel data import
- 🔐 JWT authentication
- 💳 Credit-based system
- 🎯 Clean Architecture implementation

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         Frontend (Firebase)         │
│          React/TypeScript           │
└──────────────┬──────────────────────┘
               │ HTTPS
               ▼
┌─────────────────────────────────────┐
│        Backend (Hostinger VPS)      │
│            FastAPI/Python           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│       Database (MongoDB Atlas)      │
│           Cloud MongoDB             │
└─────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Server**: Gunicorn + Uvicorn
- **Database**: MongoDB Atlas
- **AI Services**: Google Gemini, HuggingFace
- **PDF Generation**: ReportLab
- **Deployment**: Hostinger VPS with Nginx

### Frontend
- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Deployment**: Firebase Hosting
- **State Management**: Native React hooks

## 📁 Project Structure

```
rapiddocs/
├── backend/
│   ├── app/
│   │   ├── domain/           # Business logic & interfaces
│   │   ├── application/      # Use cases & DTOs
│   │   ├── infrastructure/   # External services
│   │   ├── presentation/     # API routes & schemas
│   │   └── main_simple.py    # Application entry
│   ├── deploy.sh             # Deployment script
│   ├── setup-vps.sh          # VPS setup script
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── ts/              # TypeScript source
│   │   ├── styles/          # CSS styles
│   │   └── index.html       # Entry HTML
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite configuration
└── README.md                # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- MongoDB Atlas account
- Google Cloud account (for Gemini API)

### Local Development

#### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn app.main_simple:app --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`

## 📦 Deployment

### Backend Deployment (Hostinger VPS)

1. **Setup VPS**:
   ```bash
   ssh root@YOUR_VPS_IP
   wget https://raw.githubusercontent.com/o42sam/rapiddocs/master/backend/setup-vps.sh
   chmod +x setup-vps.sh
   ./setup-vps.sh
   ```

2. **Deploy Application**:
   ```bash
   ./deploy.sh --host YOUR_VPS_IP --user root
   ```

3. **Configure Environment**:
   - Edit `/home/docgen/backend/.env.production`
   - Add MongoDB URL, API keys, JWT secrets

See [HOSTINGER_BACKEND_DEPLOYMENT.md](HOSTINGER_BACKEND_DEPLOYMENT.md) for detailed instructions.

### Frontend Deployment (Firebase)

1. **Initialize Firebase**:
   ```bash
   cd frontend
   npm install -g firebase-tools
   firebase login
   firebase init
   ```

2. **Build and Deploy**:
   ```bash
   npm run build
   firebase deploy
   ```

See [FIREBASE_FRONTEND_DEPLOYMENT.md](FIREBASE_FRONTEND_DEPLOYMENT.md) for detailed instructions.

## 🔑 Environment Variables

### Backend (.env)
```bash
# MongoDB
MONGODB_URL=your_mongodb_url
MONGODB_DB_NAME=docgen_prod

# AI Services
GEMINI_API_KEY=your_gemini_key
HUGGINGFACE_API_KEY=your_hf_key

# JWT Security
JWT_SECRET_KEY=generate_with_secrets
JWT_REFRESH_SECRET_KEY=generate_different_secret

# CORS
CORS_ORIGINS=https://yourapp.web.app
```

### Frontend (.env)
```bash
VITE_API_URL=https://api.yourdomain.com/api/v1
VITE_GOOGLE_CLIENT_ID=your_google_client_id
```

## 📚 API Documentation

Once deployed, visit:
- API Docs: `https://api.yourdomain.com/api/v1/docs`
- Health Check: `https://api.yourdomain.com/health`

### Main Endpoints
- `POST /api/v1/generate/document` - Generate document
- `GET /api/v1/generate/status/{job_id}` - Check generation status
- `GET /api/v1/generate/download/{job_id}` - Download generated document
- `GET /api/v1/credits/balance` - Check credit balance

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## 🔒 Security

- JWT-based authentication
- Rate limiting on API endpoints
- CORS protection
- SSL/TLS encryption
- Input validation and sanitization
- MongoDB connection encryption
- Environment variable protection

## 📈 Monitoring

### Health Checks
- Basic: `/health`
- Detailed: `/health/detailed`
- Readiness: `/health/ready`

### Logs
- Backend: `/var/log/docgen/`
- Nginx: `/var/log/nginx/`
- Service: `journalctl -u docgen-backend`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is proprietary software. All rights reserved.

## 👥 Authors

- **Your Name** - Initial work

## 🙏 Acknowledgments

- Google Gemini for AI text generation
- HuggingFace for image generation
- MongoDB Atlas for database hosting
- Firebase for frontend hosting
- Hostinger for VPS hosting

## 📞 Support

For support, email support@rapiddocs.io or open an issue.

## 🚦 Status

- Backend: ![Backend](https://img.shields.io/badge/Backend-Ready-green)
- Frontend: ![Frontend](https://img.shields.io/badge/Frontend-Ready-green)
- Database: ![Database](https://img.shields.io/badge/Database-Connected-green)
- Production: ![Production](https://img.shields.io/badge/Production-Ready-green)

## 🔗 Links

- [Backend Deployment Guide](HOSTINGER_BACKEND_DEPLOYMENT.md)
- [Frontend Deployment Guide](FIREBASE_FRONTEND_DEPLOYMENT.md)
- [API Documentation](https://api.rapiddocs.io/api/v1/docs)
- [Live Demo](https://rapiddocs.web.app)

---

**Version**: 1.0.0
**Last Updated**: January 2025