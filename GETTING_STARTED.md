# Getting Started with Document Generator

This guide will help you set up and run the Document Generator application.

## Prerequisites

Before you begin, make sure you have the following installed:

- **Python 3.10+** - [Download here](https://www.python.org/downloads/)
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **MongoDB Atlas Account** - [Sign up here](https://www.mongodb.com/cloud/atlas)
- **Hugging Face Account** - [Sign up here](https://huggingface.co/)

## Step 1: Clone or Navigate to the Project

```bash
cd /home/taliban/doc-gen
```

## Step 2: Get Your API Credentials

### MongoDB Atlas Setup

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster (free tier is fine)
3. Create a database user with read/write permissions
4. Whitelist your IP address (or use 0.0.0.0/0 for development)
5. Get your connection string (it looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

### Hugging Face API Key

1. Go to [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. Click "New token"
3. Give it a name (e.g., "DocGenerator")
4. Select "Read" permissions
5. Copy the token (starts with `hf_...`)

## Step 3: Run the Setup Script

```bash
./setup.sh
```

This script will:
- Create a Python virtual environment
- Install all backend dependencies
- Install all frontend dependencies
- Create `.env` files from templates

## Step 4: Configure Environment Variables

Edit `backend/.env` and add your credentials:

```bash
# MongoDB Atlas
MONGODB_URL=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/
MONGODB_DB_NAME=docgen

# Hugging Face
HUGGINGFACE_API_KEY=hf_your_api_key_here
```

**Important:** Replace the placeholders with your actual credentials.

## Step 5: Start the Application

### Option A: Use the Helper Scripts (Recommended)

**Terminal 1 - Start Backend:**
```bash
./start-backend.sh
```

**Terminal 2 - Start Frontend:**
```bash
./start-frontend.sh
```

### Option B: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Step 6: Access the Application

Once both servers are running:

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/api/v1/docs

## Using the Application

1. **Enter Document Description:** Describe what kind of document you want to generate
2. **Set Document Length:** Choose between 500-5000 words
3. **Upload Company Logo (Optional):** Add your company branding
4. **Select Color Theme:** Choose from 5 predefined themes
5. **Add Statistics (Optional):** Add up to 10 company statistics with visualizations
6. **Click Generate:** Wait 1-3 minutes for your document to be generated
7. **Download PDF:** Once complete, download your professional PDF document

## Example Usage

Here's an example of what you might enter:

**Description:**
```
Create a quarterly business report for a tech startup. Focus on our growth in
the AI/ML sector, highlighting our innovative products and expanding customer base.
Include sections on market analysis, product development, and future outlook.
```

**Length:** `2000` words

**Statistics:**
- Revenue Growth: `45.2%` (Bar chart)
- Customer Satisfaction: `4.8/5` (Gauge)
- Market Share: `12.5%` (Pie chart)
- Monthly Active Users: `50000` (Line chart)

**Color Theme:** Ocean Blue

## Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError` when starting backend

**Solution:** Make sure you activated the virtual environment:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Problem:** `MongoDB connection failed`

**Solution:**
- Check your MongoDB Atlas connection string in `.env`
- Verify your IP is whitelisted in MongoDB Atlas
- Make sure your database user has proper permissions

**Problem:** `Hugging Face API error`

**Solution:**
- Verify your API key is correct in `.env`
- Check if the models are accessible (some require approval)
- Wait a few seconds if you see "Model is loading" - this is normal

### Frontend Issues

**Problem:** `Cannot connect to backend`

**Solution:**
- Make sure the backend is running on port 8000
- Check `frontend/.env` has correct `VITE_API_BASE_URL`
- Check for CORS errors in browser console

**Problem:** `npm install` fails

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Generation Issues

**Problem:** Document generation takes too long or fails

**Solution:**
- Hugging Face models may need to "warm up" (first request takes longer)
- Try reducing document length or number of statistics
- Check backend logs for specific error messages

**Problem:** Images not generating

**Solution:**
- This is usually due to model loading time
- The document will still be generated, just without AI images
- Check backend logs for image generation errors

## Model Information

The application uses these Hugging Face models:

- **Text Generation:** `mistralai/Mistral-7B-Instruct-v0.2`
  - Professional document writing
  - Context-aware content generation

- **Image Generation:** `black-forest-labs/FLUX.1-schnell`
  - Fast generation (4 steps)
  - High-quality images
  - Free to use

## Project Structure

```
doc-gen/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── models/   # Database models
│   │   ├── schemas/  # API schemas
│   │   ├── services/ # Business logic
│   │   └── routes/   # API endpoints
│   ├── uploads/      # Uploaded files
│   └── generated_pdfs/ # Output PDFs
├── frontend/         # TypeScript + Tailwind frontend
│   └── src/
│       ├── ts/       # TypeScript code
│       └── styles/   # CSS styles
└── CLAUDE.md        # Detailed specification

```

## Next Steps

- Customize color themes in `frontend/src/ts/types/document.ts`
- Adjust PDF styling in `backend/app/services/pdf_generator.py`
- Add more visualization types in `backend/app/services/visualization.py`
- Deploy to production (see CLAUDE.md for deployment guide)

## Support

For issues or questions:
1. Check the logs in the terminal where servers are running
2. Review the API documentation at http://localhost:8000/api/v1/docs
3. Refer to CLAUDE.md for detailed technical documentation

## Tips for Best Results

1. **Be specific in descriptions:** More detail = better content
2. **Choose appropriate length:** Longer documents take more time
3. **Use relevant statistics:** They will be integrated into the text
4. **Pick complementary colors:** Theme colors should work well together
5. **Wait patiently:** First-time generation may take 2-3 minutes

Happy document generating! 🚀
