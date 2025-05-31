# CLAUDE.md - Real Estate CRM Project Configuration

## Project Overview
Comprehensive Real Estate CRM system with AI integration for Narissa Realty - provides complete client management, transaction tracking, and intelligent workflow automation.

## Quick Commands
```bash
# CRM Development
python real_estate_crm.py        # Start main Flask CRM application
source venv/bin/activate         # Activate Python environment
python app.py                    # Start legacy Flask application

# Database Management
sqlite3 real_estate.db ".schema" # View database schema
python -c "import sqlite3; print('Database ready')"  # Test database connection

# Static Demo
open C:/Users/ender/Desktop/CRM_Demo/index.html  # Open static HTML demo (Windows)

# AI Integration Development
python email_processor.py        # Test email processing capabilities
python workflow_automation.py    # Test AI workflow features

# PDF Processing (Research Track)
python analyze_forms.py          # Analyze PDF form structures
python advanced_pdf_reconstructor.py  # Multi-strategy PDF reconstruction
python professional_pdf_filler.py     # Professional coordinate-based filling

# File Management
ls -la *.sql                     # View database schema files
ls -la templates/                # View HTML templates
rm -rf __pycache__/ *.pyc        # Clean Python cache files

# Project Documentation
cat memory-bank/system_manifest.md  # View system architecture
cat memory-bank/project_roadmap.md  # View development roadmap
cat memory-bank/crm_core_module.md  # View CRM core documentation
```

## Code Style Guidelines
- **Python**: Follow PEP 8 standards
- **Flask**: Use blueprints for modular CRM features
- **Database**: Use SQLAlchemy ORM for database operations
- **AI Integration**: Modular design for AI components
- **Error Handling**: Comprehensive exception handling for all operations
- **API Design**: RESTful endpoints for all CRM operations
- **Frontend**: Responsive design with Bootstrap framework

## Testing Workflow
- Test all CRUD operations for clients, properties, transactions
- Validate database integrity and relationships
- Test responsive design on desktop, tablet, and mobile
- Verify AI integration with sample email data
- Test static HTML demo functionality with localStorage
- Validate security features and user authentication

## Dependencies
```bash
pip install -r requirements.txt
```
Key libraries: Flask, SQLAlchemy, Bootstrap, jQuery, AI/ML libraries

## Architecture Notes
- **CRM Core**: 177-field database schema with complete relationship management
- **Dual Interface**: Flask web app + static HTML demo
- **AI Integration**: Email processing, workflow automation, predictive analytics
- **Security**: Authentication, authorization, data encryption
- **Deployment**: Cloud-ready with production hosting support

## Repository Structure
- `real_estate_crm.py` - Main Flask CRM application
- `real_estate_crm_schema.sql` - Complete 177-field database schema
- `templates/` - HTML templates for CRM interface
- `static/` - CSS/JS assets for responsive design
- `memory-bank/` - Comprehensive system documentation
- `C:\Users\ender\Desktop\CRM_Demo\` - Static HTML demo system
- PDF processing files - Research track for form automation

## Business Context
- **Client**: Narissa Realty (sister's business)
- **Primary Focus**: Complete CRM system for real estate professionals
- **Secondary Focus**: AI-powered automation and intelligence
- **Research Track**: PDF form processing and legal compliance
- **Users**: Real estate agents, teams, and agencies

## Development Priorities
1. **CRM Optimization**: Core functionality testing and refinement
2. **AI Integration**: Email processing and workflow automation
3. **Production Deployment**: Hosting, security, and performance
4. **User Experience**: Interface improvements and mobile optimization

## Branch Progress Tracking Implementation
This project implements the new Branch Progress Tracking workflow:
- **Source**: `BRANCH_README.md` defines Phase 2 AI Integration success criteria
- **Execution**: `/task` command automatically updates branch progress on every completion
- **Integration**: Progress tracked in both granular tasks and high-level branch milestones
- **Accountability**: Real-time updates ensure branch plans stay current with actual development

### Current Branch: feature/phase-2-ai-integration
- **Goal**: AI-enhanced chatbot with email processing capabilities
- **Progress Tracking**: Automatic updates to BRANCH_README.md on task completion
- **Success Criteria**: 5 major deliverables with 10 supporting tasks
- **Timeline**: 3-week development cycle with milestone tracking