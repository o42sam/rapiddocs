# Document Generator Web App

A sophisticated web application that programmatically generates professional PDF documents using AI-powered text and image generation.

## Features

- AI-powered document text generation using Hugging Face models
- AI-generated images matching document context
- Custom color themes (3-color palettes)
- Dynamic company statistics with data visualizations
- Company logo integration
- Professional PDF output with styled layouts

## Tech Stack

**Backend:**
- FastAPI (Python)
- MongoDB Atlas
- Hugging Face API (Mistral-7B, FLUX.1)
- ReportLab (PDF generation)
- Matplotlib (Data visualization)

**Frontend:**
- TypeScript
- HTML5
- Tailwind CSS
- Vite

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB Atlas account
- Hugging Face API key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn app.main:app --reload
```

Backend runs on http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env if needed
npm run dev
```

Frontend runs on http://localhost:5173

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

See [CLAUDE.md](./CLAUDE.md) for detailed documentation.

## License

MIT
