# Document Generator Web App

A sophisticated web application that programmatically generates professional PDF documents using AI-powered text and image generation, with customizable design specifications and data visualizations.

## Project Overview

This application allows users to generate professional PDF documents by providing:
- Document description prompts for AI text generation
- Custom design specifications (color themes, layouts)
- Company branding (logo upload)
- Company statistics (dynamic fields with visualizations)
- Configurable document length

The system uses Hugging Face models for content generation and creates data visualizations that are seamlessly integrated into the final PDF document.

## Architecture

### Project Structure

```
doc-gen/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Configuration and environment variables
│   │   ├── database.py             # MongoDB Atlas connection
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── document.py         # Document data models
│   │   │   └── user.py             # User data models
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── document.py         # Pydantic schemas for documents
│   │   │   └── request.py          # API request/response schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── text_generation.py  # Hugging Face text generation
│   │   │   ├── image_generation.py # Hugging Face image generation
│   │   │   ├── visualization.py    # Data visualization generation
│   │   │   ├── pdf_generator.py    # PDF document assembly
│   │   │   └── storage.py          # File storage (S3/local)
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── documents.py        # Document CRUD endpoints
│   │   │   ├── generation.py       # Generation endpoints
│   │   │   └── upload.py           # File upload endpoints
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── color.py            # Color theme utilities
│   │       └── validation.py       # Input validation
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── index.html              # Main HTML file
│   │   ├── styles/
│   │   │   ├── main.css            # Tailwind imports and custom styles
│   │   │   └── components.css      # Component-specific styles
│   │   ├── ts/
│   │   │   ├── main.ts             # Application entry point
│   │   │   ├── api/
│   │   │   │   ├── client.ts       # API client configuration
│   │   │   │   └── endpoints.ts    # API endpoint functions
│   │   │   ├── components/
│   │   │   │   ├── ColorPalette.ts # Color picker component
│   │   │   │   ├── StatisticsForm.ts # Dynamic statistics input
│   │   │   │   ├── DocumentForm.ts  # Main document generation form
│   │   │   │   └── PreviewPanel.ts  # Document preview
│   │   │   ├── types/
│   │   │   │   ├── document.ts     # Document type definitions
│   │   │   │   └── api.ts          # API type definitions
│   │   │   └── utils/
│   │   │       ├── validation.ts   # Form validation
│   │   │       └── formatter.ts    # Data formatting utilities
│   │   └── assets/
│   │       └── images/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── README.md
├── CLAUDE.md                        # This file
├── .gitignore
└── README.md
```

## Technical Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: MongoDB Atlas
- **AI Models**: Hugging Face Inference API
  - Text Generation: `mistralai/Mistral-7B-Instruct-v0.2` or `meta-llama/Llama-2-7b-chat-hf`
  - Image Generation: `stabilityai/stable-diffusion-xl-base-1.0` or `black-forest-labs/FLUX.1-schnell`
- **PDF Generation**: ReportLab or WeasyPrint
- **Data Visualization**: Matplotlib, Plotly, or Seaborn
- **File Storage**: Local filesystem or AWS S3
- **Image Processing**: Pillow

### Frontend
- **Languages**: TypeScript, HTML5
- **Styling**: Tailwind CSS
- **Build Tool**: Vite or Webpack
- **HTTP Client**: Axios or Fetch API
- **Color Picker**: Custom component with Tailwind colors

## Core Features

### 1. Document Generation Form

**UI Components**:
- Text area for document description prompt
- Number input for document length (word count: 500-5000 words)
- File upload for company logo (PNG, JPG, SVG - max 5MB)
- Dynamic statistics form (add/remove fields)
- Color theme selector (3-color palette)
- Generate button with loading state

**Form Fields**:
```typescript
interface DocumentGenerationRequest {
  description: string;           // Document description prompt
  length: number;                 // Target word count
  companyLogo?: File;             // Logo file upload
  statistics: Statistic[];        // Array of statistics
  designSpec: DesignSpecification;
}

interface Statistic {
  id: string;
  name: string;                   // e.g., "Revenue Growth"
  value: number;                  // e.g., 25.5
  unit?: string;                  // e.g., "%", "$M", "users"
  visualizationType: 'bar' | 'line' | 'pie' | 'gauge';
}

interface DesignSpecification {
  backgroundColor: string;        // Default: #FFFFFF
  foregroundColor1: string;       // Primary accent color
  foregroundColor2: string;       // Secondary accent color
  colorThemeName?: string;        // e.g., "Ocean Blue", "Corporate Red"
}
```

### 2. Color Theme Selection

**Predefined Themes** (Tailwind-based):
- **Ocean Blue**: Background: white, FG1: blue-600, FG2: cyan-500
- **Corporate Red**: Background: white, FG1: red-600, FG2: orange-500
- **Forest Green**: Background: white, FG1: green-600, FG2: teal-500
- **Royal Purple**: Background: white, FG1: purple-600, FG2: pink-500
- **Sunset Orange**: Background: white, FG1: orange-600, FG2: yellow-500
- **Custom**: User-defined color picker

**UI Features**:
- Visual color swatches
- Live preview of color combinations
- Accessibility contrast checker

### 3. Dynamic Statistics Input

**Features**:
- Add/remove statistic fields dynamically
- Each statistic includes:
  - Name (text input)
  - Value (number input)
  - Unit (optional text)
  - Visualization type selector
- Minimum 0, maximum 10 statistics per document
- Real-time validation

### 4. AI-Powered Content Generation

**Text Generation**:
- Model: `mistralai/Mistral-7B-Instruct-v0.2` (recommended for document generation)
- Prompt engineering includes:
  - Document description
  - Target length
  - Company statistics context
  - Professional tone instructions
  - Section structure guidance

**Prompt Template**:
```
You are a professional document writer. Generate a comprehensive business document based on the following:

Description: {user_description}
Target Length: {word_count} words
Company Statistics: {formatted_statistics}

Requirements:
- Professional and formal tone
- Include sections: Executive Summary, Introduction, Main Content, Statistics Analysis, Conclusion
- Integrate the provided statistics naturally into the content
- Use clear headings and subheadings
- Ensure content is coherent and well-structured

Generate the document:
```

**Image Generation**:
- Model: `black-forest-labs/FLUX.1-schnell` (fast, high-quality, free)
- Generate 1-3 relevant images based on document context
- Images are styled to match the color theme
- Prompt includes document theme and visual style preferences

**Image Prompt Template**:
```
Professional business illustration for a document about {document_theme}.
Style: clean, modern, corporate.
Color palette: {foreground_color_1}, {foreground_color_2}.
High quality, suitable for business presentation.
```

### 5. Data Visualization

**Library**: Matplotlib with custom styling

**Visualization Types**:
- **Bar Chart**: Comparing multiple statistics
- **Line Chart**: Trends or time-based data
- **Pie Chart**: Percentage breakdowns
- **Gauge Chart**: Single metric with target ranges

**Styling**:
- Match document color theme
- Professional appearance
- High DPI for PDF quality (300 DPI)
- Consistent sizing and layout

**Implementation**:
```python
def generate_visualization(statistic: Statistic, colors: DesignSpec) -> bytes:
    """Generate a chart image based on statistic data and design specs"""
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

    # Apply color theme
    plt.rcParams['axes.prop_cycle'] = plt.cycler(
        color=[colors.foreground_color_1, colors.foreground_color_2]
    )

    # Generate appropriate chart type
    if statistic.visualization_type == 'bar':
        # Bar chart logic
    elif statistic.visualization_type == 'pie':
        # Pie chart logic
    # ... etc

    # Export to bytes
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    return buffer.getvalue()
```

### 6. PDF Document Assembly

**PDF Structure**:
```
1. Cover Page
   - Company logo (top-right or center)
   - Document title (extracted from content)
   - Generation date
   - Color accent banner (foreground_color_1)

2. Table of Contents
   - Auto-generated from headings

3. Executive Summary
   - First 200 words of generated content

4. Main Content Sections
   - Generated text with proper formatting
   - Headings styled with foreground colors
   - AI-generated images embedded appropriately

5. Statistics Section
   - Each statistic presented with:
     * Description from generated text
     * Visualization chart
     * Key insights

6. Conclusion
   - Final section of generated text

7. Footer
   - Page numbers
   - Generation timestamp
   - Subtle color accent
```

**PDF Generation Library**: ReportLab (recommended)

**Styling**:
- Font: Professional sans-serif (e.g., Helvetica, Arial)
- Margins: 1 inch on all sides
- Headings: Larger font, bold, colored with foreground colors
- Body text: 11pt, black on white
- Color accents: Headers, dividers, callout boxes

### 7. Backend API Endpoints

**Generation Endpoints**:

```python
# POST /api/v1/generate/document
# Request Body: DocumentGenerationRequest (multipart/form-data)
# Response: { "job_id": "uuid", "status": "processing" }

# GET /api/v1/generate/status/{job_id}
# Response: { "status": "completed|processing|failed", "progress": 0-100 }

# GET /api/v1/generate/download/{job_id}
# Response: PDF file download

# POST /api/v1/generate/preview
# Generate a quick preview without full processing
```

**Document Management**:

```python
# GET /api/v1/documents
# List all generated documents for user

# GET /api/v1/documents/{doc_id}
# Get document metadata

# DELETE /api/v1/documents/{doc_id}
# Delete document and associated files
```

**Upload Endpoints**:

```python
# POST /api/v1/upload/logo
# Upload company logo, return file URL

# POST /api/v1/upload/validate
# Validate file before upload (size, format)
```

### 8. Database Schema (MongoDB)

**Documents Collection**:
```javascript
{
  _id: ObjectId,
  user_id: String,  // For future multi-user support
  title: String,
  description: String,
  status: String,  // "processing", "completed", "failed"
  config: {
    length: Number,
    statistics: [
      {
        name: String,
        value: Number,
        unit: String,
        visualization_type: String
      }
    ],
    design_spec: {
      background_color: String,
      foreground_color_1: String,
      foreground_color_2: String,
      theme_name: String
    }
  },
  files: {
    logo_url: String,
    pdf_url: String,
    generated_images: [String],
    visualizations: [String]
  },
  generation_metadata: {
    text_model: String,
    image_model: String,
    word_count: Number,
    generation_time_seconds: Number
  },
  created_at: DateTime,
  updated_at: DateTime,
  completed_at: DateTime
}
```

**Generation Jobs Collection**:
```javascript
{
  _id: ObjectId,
  document_id: ObjectId,
  status: String,
  progress: Number,  // 0-100
  current_step: String,  // "generating_text", "generating_images", etc.
  error_message: String,
  created_at: DateTime,
  updated_at: DateTime
}
```

## Implementation Flow

### Document Generation Pipeline

1. **Request Received**
   - Validate input data
   - Upload and process company logo
   - Create database record
   - Return job_id to client

2. **Text Generation**
   - Construct prompt with context
   - Call Hugging Face text generation API
   - Parse and structure generated content
   - Extract section headings
   - Update progress: 30%

3. **Image Generation**
   - Extract key themes from generated text
   - Generate 1-3 contextual images
   - Apply color theme to prompts
   - Download and store images
   - Update progress: 50%

4. **Data Visualization**
   - Create chart for each statistic
   - Apply color theme
   - Export as high-res PNG
   - Store visualization files
   - Update progress: 70%

5. **PDF Assembly**
   - Initialize PDF document
   - Add cover page with logo
   - Generate table of contents
   - Insert formatted text content
   - Embed images and visualizations
   - Apply styling and color theme
   - Update progress: 90%

6. **Finalization**
   - Save PDF to storage
   - Update database with file URLs
   - Mark job as completed
   - Update progress: 100%

## Environment Configuration

### Backend `.env`

```bash
# Application
APP_NAME=DocGenerator
APP_ENV=development
DEBUG=True
API_PREFIX=/api/v1

# MongoDB Atlas
MONGODB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/
MONGODB_DB_NAME=docgen

# Hugging Face
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxx
TEXT_GENERATION_MODEL=mistralai/Mistral-7B-Instruct-v0.2
IMAGE_GENERATION_MODEL=black-forest-labs/FLUX.1-schnell

# File Storage
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=5242880  # 5MB in bytes
ALLOWED_IMAGE_FORMATS=png,jpg,jpeg,svg

# PDF Generation
PDF_OUTPUT_DIR=./generated_pdfs
PDF_DPI=300

# API Rate Limiting
RATE_LIMIT_PER_MINUTE=10

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend `.env`

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_MAX_FILE_SIZE=5242880
VITE_SUPPORTED_FORMATS=image/png,image/jpeg,image/svg+xml
```

## Key Libraries and Dependencies

### Backend (`requirements.txt`)

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
motor==3.3.2  # Async MongoDB driver
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0

# AI/ML
huggingface-hub==0.20.2
requests==2.31.0

# PDF Generation
reportlab==4.0.9
# OR weasyprint==60.2

# Data Visualization
matplotlib==3.8.2
seaborn==0.13.1
plotly==5.18.0

# Image Processing
Pillow==10.2.0

# Utilities
python-jose[cryptography]==3.3.0  # For future auth
passlib[bcrypt]==1.7.4  # For future auth
aiofiles==23.2.1
```

### Frontend (`package.json`)

```json
{
  "dependencies": {
    "axios": "^1.6.5",
    "@types/node": "^20.11.5"
  },
  "devDependencies": {
    "typescript": "^5.3.3",
    "vite": "^5.0.11",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.33",
    "autoprefixer": "^10.4.17",
    "@types/axios": "^0.14.0"
  }
}
```

## API Request/Response Examples

### Generate Document

**Request**:
```http
POST /api/v1/generate/document
Content-Type: multipart/form-data

{
  "description": "Create a quarterly business report highlighting our company's growth in the tech sector, focusing on innovation and market expansion.",
  "length": 2000,
  "logo": <file>,
  "statistics": [
    {
      "name": "Revenue Growth",
      "value": 32.5,
      "unit": "%",
      "visualization_type": "bar"
    },
    {
      "name": "Customer Satisfaction",
      "value": 4.7,
      "unit": "/5",
      "visualization_type": "gauge"
    },
    {
      "name": "Market Share",
      "value": 18.3,
      "unit": "%",
      "visualization_type": "pie"
    }
  ],
  "design_spec": {
    "background_color": "#FFFFFF",
    "foreground_color_1": "#2563EB",
    "foreground_color_2": "#06B6D4",
    "theme_name": "Ocean Blue"
  }
}
```

**Response**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Document generation started",
  "estimated_time_seconds": 120
}
```

### Check Status

**Request**:
```http
GET /api/v1/generate/status/550e8400-e29b-41d4-a716-446655440000
```

**Response**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 65,
  "current_step": "generating_visualizations",
  "document_id": "65a1b2c3d4e5f6789abcdef0"
}
```

### Download Document

**Request**:
```http
GET /api/v1/generate/download/550e8400-e29b-41d4-a716-446655440000
```

**Response**:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="Business_Report_2025-01-15.pdf"

<PDF binary data>
```

## UI/UX Considerations

### Responsive Design
- Mobile-first approach with Tailwind
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Form adapts to screen size
- Preview panel collapses on mobile

### User Feedback
- Loading states with progress indicators
- Real-time validation messages
- Success/error notifications (toast messages)
- Estimated generation time display

### Accessibility
- ARIA labels on all form controls
- Keyboard navigation support
- Color contrast compliance (WCAG AA)
- Screen reader friendly

### Progressive Enhancement
- Works without JavaScript (basic form submission)
- Enhanced with TypeScript for better UX
- Graceful degradation for older browsers

## Error Handling

### Backend
- Validation errors: 400 Bad Request
- Authentication errors: 401 Unauthorized
- Not found: 404 Not Found
- Server errors: 500 Internal Server Error
- Rate limiting: 429 Too Many Requests

### Frontend
- Network error handling with retry logic
- Form validation before submission
- Clear error messages to user
- Fallback UI for failed states

## Security Considerations

1. **File Upload Security**
   - Validate file types and sizes
   - Scan for malicious content
   - Store with randomized names
   - Limit upload rate

2. **API Security**
   - Rate limiting on all endpoints
   - Input sanitization
   - CORS configuration
   - API key rotation for HuggingFace

3. **Data Privacy**
   - Secure MongoDB connection (TLS)
   - Environment variable protection
   - Temporary file cleanup
   - Optional user authentication for production

## Testing Strategy

### Backend Tests
- Unit tests for services
- Integration tests for API endpoints
- Mock HuggingFace API calls
- Database operation tests

### Frontend Tests
- Component unit tests
- Form validation tests
- API integration tests
- E2E tests with Playwright/Cypress

## Deployment Considerations

### Backend Deployment
- Containerize with Docker
- Deploy to AWS ECS, Google Cloud Run, or Railway
- Environment-specific configurations
- Background job processing (Celery/Redis for queue)

### Frontend Deployment
- Build static assets with Vite
- Deploy to Vercel, Netlify, or CloudFlare Pages
- CDN for asset delivery
- Environment variable configuration

### Database
- MongoDB Atlas (already cloud-hosted)
- Regular backups
- Index optimization for queries

## Future Enhancements

1. **User Authentication**
   - User accounts and login
   - Document history per user
   - API key management

2. **Templates**
   - Pre-built document templates
   - Custom template creation
   - Template marketplace

3. **Collaboration**
   - Share documents
   - Commenting system
   - Version history

4. **Advanced Features**
   - Multi-language support
   - Custom fonts
   - Interactive PDFs
   - Document editing after generation

5. **Analytics**
   - Generation metrics
   - Popular themes tracking
   - Usage statistics dashboard

## Getting Started

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

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with API URL
npm run dev
```

### MongoDB Atlas Setup
1. Create account at mongodb.com/atlas
2. Create new cluster
3. Create database user
4. Whitelist IP addresses
5. Get connection string
6. Add to backend .env

### HuggingFace Setup
1. Create account at huggingface.co
2. Generate API token (Settings → Access Tokens)
3. Add to backend .env
4. Verify model access (some models require approval)

## Support and Documentation

- **API Documentation**: Auto-generated at `/docs` (Swagger UI)
- **Technical Support**: Create issues in project repository
- **Model Documentation**:
  - Text: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
  - Image: https://huggingface.co/black-forest-labs/FLUX.1-schnell

## License

To be determined based on project requirements.

---

**Version**: 1.0.0
**Last Updated**: 2025-01-05
**Maintained By**: Development Team
