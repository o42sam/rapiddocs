# Document Type User Guide

## Overview

The document generation system now supports two types of documents:

### 1. Formal Documents
- **Use Case**: Professional business documents, reports, white papers, proposals
- **Content**: Text-only with professional formatting
- **Features**:
  - ✅ AI-generated text content
  - ✅ Company logo on cover page
  - ✅ Professional formatting with headings and sections
  - ✅ Statistics mentioned in text
  - ✅ 3 vertical decorative lines on right edge (alternating theme colors, varying thickness)
  - ❌ No AI-generated images
  - ❌ No data visualization charts
- **Generation Time**: ~60 seconds
- **Best For**: Formal reports, legal documents, academic papers, executive summaries

### 2. Infographic Documents
- **Use Case**: Visual presentations, marketing materials, data-driven reports
- **Content**: Rich multimedia content with visuals and charts
- **Features**:
  - ✅ AI-generated text content
  - ✅ Company logo on cover page
  - ✅ Professional formatting with headings and sections
  - ✅ Statistics mentioned in text
  - ✅ 2 AI-generated images based on document theme
  - ✅ Data visualization charts for each statistic
  - ✅ Clean page design (no edge decorations)
- **Generation Time**: ~120 seconds
- **Best For**: Annual reports, investor presentations, marketing materials, dashboards

## How to Use

### API Request Format

The document type is specified using the `document_type` parameter in the form data:

```bash
POST /api/v1/generate/document
Content-Type: multipart/form-data

Fields:
- description: (string, required) Document description/theme
- length: (integer, required) Target word count (500-5000)
- document_type: (string, optional) "formal" or "infographic" (default: "infographic")
- statistics: (JSON string, required) Array of statistics
- design_spec: (JSON string, required) Design specifications
- logo: (file, optional) Company logo image
```

### Example 1: Formal Document

```bash
curl -X POST "http://localhost:8000/api/v1/generate/document" \
  -F "description=Generate a comprehensive quarterly business performance report analyzing our company's growth in the tech sector" \
  -F "length=2000" \
  -F "document_type=formal" \
  -F 'statistics=[
    {"name":"Revenue Growth","value":32.5,"unit":"%","visualization_type":"bar"},
    {"name":"Customer Satisfaction","value":4.7,"unit":"/5","visualization_type":"gauge"},
    {"name":"Market Share","value":18.3,"unit":"%","visualization_type":"pie"}
  ]' \
  -F 'design_spec={
    "background_color":"#FFFFFF",
    "foreground_color_1":"#2563EB",
    "foreground_color_2":"#06B6D4",
    "theme_name":"Ocean Blue"
  }' \
  -F "logo=@company_logo.png"
```

**Result**: A professional text-only document with blue color accents and company logo.

### Example 2: Infographic Document

```bash
curl -X POST "http://localhost:8000/api/v1/generate/document" \
  -F "description=Create an engaging annual report showcasing our company's achievements and growth" \
  -F "length=1500" \
  -F "document_type=infographic" \
  -F 'statistics=[
    {"name":"Annual Revenue","value":25.8,"unit":"M USD","visualization_type":"line"},
    {"name":"Employee Growth","value":145,"unit":"employees","visualization_type":"bar"},
    {"name":"Customer Retention","value":94.2,"unit":"%","visualization_type":"gauge"}
  ]' \
  -F 'design_spec={
    "background_color":"#FFFFFF",
    "foreground_color_1":"#DC2626",
    "foreground_color_2":"#FB923C",
    "theme_name":"Corporate Red"
  }' \
  -F "logo=@company_logo.png"
```

**Result**: A rich document with text, 2 AI-generated images, and 3 data visualization charts.

## Response Format

Both document types return the same response format:

```json
{
  "job_id": "65a1b2c3d4e5f6789abcdef0",
  "status": "processing",
  "message": "Document generation started (formal type)",
  "estimated_time_seconds": 60
}
```

## Checking Generation Status

Use the job_id to check the status:

```bash
GET /api/v1/generate/status/{job_id}
```

Response:

```json
{
  "job_id": "65a1b2c3d4e5f6789abcdef0",
  "document_id": "65a1b2c3d4e5f6789abcdef1",
  "status": "completed",
  "progress": 100,
  "current_step": "completed",
  "error_message": null
}
```

## Downloading the Document

Once completed, download the PDF:

```bash
GET /api/v1/generate/download/{job_id}
```

Returns: PDF file

## Document Type Comparison

| Feature | Formal | Infographic |
|---------|--------|-------------|
| AI Text Generation | ✅ | ✅ |
| Professional Formatting | ✅ | ✅ |
| Company Logo | ✅ | ✅ |
| Color Themes | ✅ | ✅ |
| Statistics in Text | ✅ | ✅ |
| Edge Decorations | ✅ (3 lines) | ❌ |
| AI-Generated Images | ❌ | ✅ (2 images) |
| Data Visualizations | ❌ | ✅ (all stats) |
| Generation Time | ~60s | ~120s |
| File Size | Smaller | Larger |
| Use Case | Formal reports | Visual presentations |

## When to Use Each Type

### Use **Formal** when:
- You need a professional, text-focused document
- The document is for formal/legal purposes
- You want faster generation
- File size needs to be minimal
- The audience prefers traditional document format
- Examples: Legal documents, academic papers, formal proposals

### Use **Infographic** when:
- You need visual impact
- Data visualization is important
- The audience prefers visual content
- Marketing or presentation purposes
- You want to highlight statistics visually
- Examples: Annual reports, marketing materials, investor decks

## Error Handling

If document generation fails, you'll receive detailed error information:

```json
{
  "job_id": "65a1b2c3d4e5f6789abcdef0",
  "status": "failed",
  "error_message": "ImageGenerationError: Image generation timed out",
  "progress": 40,
  "current_step": "generating_images"
}
```

**Note**: For infographic documents, if image or visualization generation fails, the system will continue and generate the document without those elements rather than failing completely.

## Validation Rules

1. **document_type**: Must be "formal" or "infographic"
   - Invalid values will return HTTP 400 error
   - Default is "infographic" if not specified

2. **Statistics**:
   - For formal documents: Statistics are mentioned in text only
   - For infographic documents: Each statistic gets a visualization

3. **Design Specifications**:
   - Applied to both document types
   - Colors affect text headings and accents
   - Infographic type also applies colors to images and charts

## Tips and Best Practices

### For Formal Documents:
- Use longer descriptions (100-200 words) for better context
- Choose 3-5 key statistics to highlight
- Target length: 1500-3000 words for comprehensive reports
- Select professional color themes (blues, grays, blacks)

### For Infographic Documents:
- Keep descriptions focused (50-100 words) for targeted visuals
- Limit to 3-5 statistics for clean visualization
- Target length: 1000-2000 words to balance text and visuals
- Use vibrant color themes for visual impact

### General Tips:
- Always provide a company logo for professional branding
- Use consistent color themes across all your documents
- Monitor generation status regularly using the status endpoint
- Check logs for detailed information if errors occur

## Troubleshooting

### Issue: Document generation is slow
- **Formal**: Should complete in ~60 seconds. Check text generation service logs.
- **Infographic**: Should complete in ~120 seconds. Check image generation and visualization logs.

### Issue: Images not appearing in infographic document
- Check logs at `logs/image_generation.log`
- Verify HuggingFace API key is valid
- Check if image generation service is accessible

### Issue: Visualizations missing
- Check logs at `logs/visualization.log`
- Verify matplotlib is properly installed
- Check statistics data format is correct

### Issue: Invalid document_type error
- Ensure document_type is exactly "formal" or "infographic" (lowercase)
- Check for typos in the parameter name

## API Integration Examples

### Python Example

```python
import requests

# Formal document
response = requests.post(
    "http://localhost:8000/api/v1/generate/document",
    data={
        "description": "Create a quarterly business report",
        "length": 2000,
        "document_type": "formal",
        "statistics": json.dumps([
            {"name": "Revenue", "value": 1.2, "unit": "M", "visualization_type": "bar"}
        ]),
        "design_spec": json.dumps({
            "foreground_color_1": "#2563EB",
            "foreground_color_2": "#06B6D4"
        })
    },
    files={"logo": open("logo.png", "rb")}
)

job_id = response.json()["job_id"]
```

### JavaScript Example

```javascript
const formData = new FormData();
formData.append('description', 'Create a quarterly business report');
formData.append('length', 2000);
formData.append('document_type', 'infographic');
formData.append('statistics', JSON.stringify([
    {name: 'Revenue', value: 1.2, unit: 'M', visualization_type: 'bar'}
]));
formData.append('design_spec', JSON.stringify({
    foreground_color_1: '#2563EB',
    foreground_color_2: '#06B6D4'
}));
formData.append('logo', logoFile);

const response = await fetch('http://localhost:8000/api/v1/generate/document', {
    method: 'POST',
    body: formData
});

const {job_id} = await response.json();
```

## Support

For issues or questions:
- Check the logs in `backend/logs/` directory
- Review `IMPLEMENTATION_SUMMARY.md` for technical details
- Check API documentation at `/docs` (Swagger UI)
