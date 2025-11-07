# Document Generator Backend

FastAPI backend for the Document Generator application.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your MongoDB Atlas and Hugging Face credentials
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /api/v1/generate/document` - Generate new document
- `GET /api/v1/generate/status/{job_id}` - Check generation status
- `GET /api/v1/generate/download/{job_id}` - Download PDF
- `GET /api/v1/documents` - List all documents
- `POST /api/v1/upload/logo` - Upload company logo

## Project Structure

```
app/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration
├── database.py          # MongoDB connection
├── models/              # Database models
├── schemas/             # Pydantic schemas
├── services/            # Business logic
├── routes/              # API routes
└── utils/               # Utilities
```
