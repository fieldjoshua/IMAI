# Dependency Tracker

This file tracks all Python dependencies used in the P.A.R.A. Life OS project.

## Core Dependencies

### AI/ML
- `anthropic>=0.18.0` - Claude API client for AI categorization

### Notion Integration
- `notion-client>=2.2.0` - Notion API client

### File System & Monitoring
- `watchdog>=3.0.0` - File system event monitoring

### Configuration
- `python-dotenv>=1.0.0` - Environment variable management

### Document Processing
- `PyPDF2>=3.0.0` - PDF text extraction
- `python-docx>=1.1.0` - Word document processing
- `Pillow>=10.0.0` - Image processing
- `pytesseract>=0.3.10` - OCR for images (optional)

### Google Services
- `google-api-python-client>=2.100.0` - Google APIs client
- `google-auth-oauthlib>=1.1.0` - OAuth2 for Google
- `google-auth-httplib2>=0.1.1` - HTTP transport for Google auth

### Calendar/Contact Processing
- `icalendar>=5.0.0` - iCalendar file parsing
- `vobject>=0.9.6.1` - vCard parsing

### Development Tools
- `pytest>=7.4.0` - Testing framework
- `black>=23.0.0` - Code formatter
- `ruff>=0.1.0` - Linter
- `mypy>=1.5.0` - Type checker

## Version History

- **Initial**: All dependencies added for MVP implementation

