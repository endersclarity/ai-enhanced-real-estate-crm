# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-Enhanced Real Estate CRM is a comprehensive system for real estate professionals with:
- Complete CRM functionality for clients, properties, and transactions
- AI-powered form generation for California Association of Realtors (CAR) forms
- Multi-strategy approach to form filling (coordinate-based, HTML replicas, bespoke forms)
- Three-tier diagnostic system for identifying and fixing critical issues

## Essential Commands

### System Management

```bash
# Start/Restart Flask Application (CRITICAL: Always use after code changes)
ps aux | grep -E "python.*flask|python.*app" | grep -v grep | awk '{print $2}' | xargs -r kill -9
source venv/bin/activate
python core_app/real_estate_crm.py > /dev/null 2>&1 &
WSL_IP=$(ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d/ -f1)
echo "✅ Flask restarted with changes - access at http://$WSL_IP:5000"

# System Diagnostics
./scripts/three-tier-diagnostics.sh    # Full diagnostic suite
./scripts/fast-diagnostics.py          # Quick health check
./scripts/health-check.sh              # Basic verification

# Docker Management
docker-compose -f docker-compose.dev.yml up -d  # Start containers
docker-compose -f docker-compose.dev.yml down   # Stop containers
docker-compose -f docker-compose.dev.yml logs   # View logs
```

### Database Operations

```bash
# Initialize Database Schema (CAUTION: May reset data)
python core_app/init_database.py

# Populate Test Data
python populate_rich_crm_data.py       # Comprehensive test data
python simple_populate_crm.py          # Basic test data
```

### Form Processing

```bash
# Test Form Generation System
python professional_form_filler.py             # Basic PDF form filling
python enhanced_professional_form_filler.py    # Enhanced form processing
python coordinate_based_form_filler.py         # Precise form field filling
python bespoke_form_creator.py                 # Custom form creation

# Validate Form Output
python validation_framework.py                 # Legal compliance validation
python validate_pdf_outputs.py                 # Verify PDF outputs
```

### AI Integration Testing

```bash
# Test AI Functionality
python ai_chatbot_integration.py               # Test AI chatbot
python core_app/zipform_ai_functions.py        # Test ZipForm functions
python demo_enhanced_architecture.py           # Test enhanced architecture
```

### Testing

```bash
# Integration Testing
python test_enhanced_integration.py            # Test full integration
python test_offer_creation.py                  # Test form generation
python test_crm_autofill_functionality.py      # Test autofill

# Browser/UI Testing
python test_browser_compatibility.py           # Test browser compatibility  
python test_quick_form_ui.py                   # Test form UI
```

## Architecture Overview

### Core Components

1. **CRM System**: Flask-based application with SQLite/PostgreSQL database
   - Located in `core_app/real_estate_crm.py`
   - 177-field schema for comprehensive real estate data
   - RESTful API endpoints for clients, properties, transactions

2. **Form Processing System**: Multi-strategy form generation
   - Coordinate-based PDF filling (`professional_form_filler.py`)
   - HTML form recreation (`html_templates/true_crpa_form.html`)
   - Form templates and field mappings (`form_templates/`)
   - 33-field CRPA template mapped from 177 CRM fields

3. **AI Integration**: Google Gemini 2.5 Flash with LangChain
   - AI function calling (`core_app/zipform_ai_functions.py`)
   - Natural language form generation
   - Intelligent data extraction and validation

4. **Three-Tier Diagnostics**: Comprehensive system monitoring
   - Fast-fail diagnostics (`scripts/fast-diagnostics.py`)
   - AI analysis (`ai-debug/`)
   - Human-in-the-loop review

### Data Flow

1. Client/Property/Transaction data in CRM database (177 fields)
2. CrmDataMapper transforms data to form-ready format (33 fields)
3. Multiple form generation strategies:
   - Professional form filler uses ReportLab for coordinate-based filling
   - HTML templates provide pixel-perfect form replicas
   - Bespoke form creator builds custom forms from scratch
4. Validation framework ensures legal compliance and data integrity
5. Final output as PDF or HTML for user

## Current System Status

The system is in critical remediation phase with several known issues:

1. **Database Schema Mismatch**: Schema in init_database.py doesn't match actual database
2. **JavaScript Dependency Conflicts**: Bootstrap 5 and jQuery compatibility issues
3. **Enhanced Architecture Integration**: CrmDataMapper functionality needs restoration
4. **UI/UX Issues**: System requires memorized IDs instead of natural language input

## Critical Files

1. **Core Application**: `core_app/real_estate_crm.py`
2. **Database Schema**: `core_app/init_database.py`
3. **Form Processors**:
   - `professional_form_filler.py`
   - `enhanced_professional_form_filler.py`
   - `coordinate_based_form_filler.py`
4. **Templates**:
   - `form_templates/california_residential_purchase_agreement_template.json`
   - `html_templates/true_crpa_form.html`
5. **AI Integration**: `core_app/zipform_ai_functions.py`
6. **Diagnostics**: `scripts/three-tier-diagnostics.sh`

## Development Workflow

### Adding New Features

1. Run diagnostics to ensure system stability
2. Make incremental changes to affected components
3. Restart Flask application after each change
4. Verify changes with appropriate test scripts
5. Run validation to ensure compliance

### Form Development

1. Use existing form template as base (`form_templates/california_residential_purchase_agreement_template.json`)
2. Map CRM fields to form fields using the CrmDataMapper pattern
3. Test form generation with `enhanced_professional_form_filler.py`
4. Validate output with `validation_framework.py`

### Fixing Critical Issues

1. **Database Schema**: Compare init_database.py with actual database structure
2. **JavaScript Dependencies**: Ensure proper Bootstrap 5 and jQuery compatibility
3. **Enhanced Architecture**: Restore CrmDataMapper functionality
4. **UI/UX**: Replace ID-based inputs with natural language/dropdown interfaces

## Environment Variables

```bash
# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=models/gemini-2.5-flash-preview-04-17

# Database Configuration
DATABASE_URL=sqlite:///core_app/real_estate_crm.db
DB_PATH=core_app/database/

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here

# Form Processing
CAR_FORMS_PATH=car_forms/
OUTPUT_PATH=output/
TEMPLATES_PATH=form_templates/
```

## Important Notes

1. **ALWAYS restart Flask after changes** - Flask auto-reload is unreliable
2. **ALWAYS use WSL IP address** for web access (not localhost)
3. Prioritize fixing critical issues before adding new features
4. The system contains extensive form processing infrastructure ready for activation
5. All database operations require user confirmation for AI tools
6. Never commit sensitive information like API keys or passwords
7. When running the application, always bind to all interfaces with `host='0.0.0.0'`