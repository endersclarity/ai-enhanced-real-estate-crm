# Offer Creator - Setup & Instructions

## Project Overview
Automated offer generation system for Narissa Realty to streamline California real estate transactions with all required disclosure documents.

## Quick Start
```bash
cd /home/ender/.claude/projects/offer-creator
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Development Setup
1. **Environment**: Python 3.8+, Flask/FastAPI, PDF processing libraries
2. **Dependencies**: PyPDF2/reportlab for PDF manipulation, Flask for web interface
3. **Testing**: Local development server, PDF form validation

## Key Components
- **PDF Forms**: 13 disclosure documents in project directory
- **Web Interface**: Form input and PDF generation
- **Data Management**: Client information storage and templates
- **PDF Automation**: Fillable form processing and output generation

## Troubleshooting
- **PDF Issues**: Ensure proper PDF library installation
- **Form Fields**: Use PDF analysis tools to identify fillable fields
- **Web Server**: Check port availability and firewall settings