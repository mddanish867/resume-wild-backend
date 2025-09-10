# Resume Optimizer API

An intelligent resume optimization service that enhances resumes based on job descriptions using Machine Learning and NLP techniques.

## Features

- **Smart Keyword Integration**: Contextually adds relevant keywords from job descriptions
- **Format Preservation**: Maintains original document structure and formatting
- **Section-Aware Processing**: Different optimization strategies for different resume sections
- **Duplicate Prevention**: Prevents keyword stuffing and duplicate content
- **PDF Conversion**: Automatic conversion of optimized resumes to PDF format
- **RESTful API**: Easy integration with web applications

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) LibreOffice for PDF conversion on Linux/Mac

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd resume-optimizer
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Download NLTK data**:
```python
python -c "import nltk; nltk.download('punkt')"
```

5. **Optional: Install SpaCy model**:
```bash
python -m spacy download en_core_web_sm
```

### Running the Application

1. **Start the server**:
```bash
python run.py
```

2. **Access the API**:
   - Server runs on `http://127.0.0.1:5000`
   - Health check: `GET /health`

## API Endpoints

### Upload Resume
```http
POST /upload/
Content-Type: multipart/form-data

Form data:
- file: DOCX file
- user_id: UUID string
```

**Response**:
```json
{
    "resume_id": "uuid",
    "message": "Resume uploaded successfully",
    "filename": "original_filename.docx",
    "status": "uploaded"
}
```

### Optimize Resume
```http
POST /optimize-resume/{resume_id}
Content-Type: application/json

{
    "user_id": "uuid",
    "job_description": "We are looking for a software developer..."
}
```

**Response**:
```json
{
    "message": "Resume optimized successfully",
    "resume_id": "uuid",
    "download_url": "/download-resume/{resume_id}",
    "keywords_added": 8,
    "status": "completed"
}
```

### Download Optimized Resume
```http
GET /download-resume/{resume_id}
```

Returns the optimized resume file (PDF or DOCX).

### Check Resume Status
```http
GET /resume-status/{resume_id}
```

**Response**:
```json
{
    "resume_id": "uuid",
    "optimization_status": "completed",
    "keywords_added": 8,
    "has_original": true,
    "has_optimized": true
}
```

### Get User Resumes
```http
GET /user-resumes/{user_id}
```

Returns all resumes for a specific user.

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Flask settings
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000

# Database
DATABASE_URL=sqlite:///resume_optimizer.db

# Security
SECRET_KEY=your-secret-key-here

# File paths
UPLOAD_FOLDER=uploads
OPTIMIZED_FOLDER=optimized
```

### Optimization Settings

Modify `instance/config.py` to adjust optimization parameters:

```python
OPTIMIZATION_SETTINGS = {
    'max_keywords_per_section': {
        'skills': 8,
        'experience': 5,
        'projects': 4,
        'summary': 3,
        'other': 2
    },
    'global_keyword_limit': 15,
    'keyword_density_limit': 0.03,  # 3% max density
}
```

## How It Works

### 1. Keyword Extraction
- Uses TF-IDF vectorization to extract relevant keywords from job descriptions
- Filters out stop words and irrelevant terms
- Prioritizes technical skills and job-specific terms

### 2. Section Detection
- Automatically identifies resume sections (Summary, Skills, Experience, etc.)
- Applies section-specific optimization strategies

### 3. Contextual Enhancement
- Skills section: Adds keywords to pipe-separated lists
- Experience section: Creates contextual sentences
- Projects section: Integrates keywords naturally
- Summary section: Adds professional statements

### 4. Quality Control
- Prevents duplicate keywords
- Maintains keyword density limits
- Preserves original formatting and structure
- Removes redundant sentences

## Project Structure

```
resume-optimizer/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── routes.py            # API endpoints
│   ├── resume_optimizer.py  # Main optimization logic
│   ├── pdf_generator.py     # PDF conversion utilities
│   └── util.py              # Helper functions
├── instance/
│   └── config.py            # Configuration settings
├── uploads/                 # Original resume storage
├── optimized/               # Optimized resume storage
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── README.md               # This file
```

## Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid input or missing required fields
- **404 Not Found**: Resume or file not found
- **500 Internal Server Error**: Processing errors with detailed messages

## Logging

Application logs are stored in the `logs/` directory:
- `app.log`: General application logs
- `errors.log`: Error-specific logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the logs in `logs/app.log`
2. Verify all dependencies are installed
3. Ensure required directories exist
4. Check file permissions

## Troubleshooting

### PDF Conversion Issues

**Windows**: Install Microsoft Word or use the reportlab fallback
```bash
pip install reportlab
```

**Linux/Mac**: Install LibreOffice
```bash
# Ubuntu/Debian
sudo apt-get install libreoffice

# macOS with Homebrew
brew install libreoffice
```

### NLTK Download Issues
```python
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
```

### Memory Issues with Large Models
If you encounter memory issues with the BERT model, you can disable it by modifying the model loading in `resume_optimizer.py`.

## Performance Tips

- Use SSD storage for faster file operations
- Increase memory for processing large resumes
- Consider using Redis for caching in production
- Implement rate limiting for production deployments