#!/usr/bin/env python3
"""
Enhanced Real Estate CRM Entry Point (Boilerplate Integration)
Combines your existing three-tier diagnostics with professional Flask patterns
"""
import os
import sys

# Add app directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import the enhanced application
from app import create_app

# Create application instance
app = create_app()

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)