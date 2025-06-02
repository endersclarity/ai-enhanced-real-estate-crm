#!/usr/bin/env python3
"""
Production entry point for Real Estate CRM
"""
import os
import sys

# Add core_app to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core_app'))

from real_estate_crm import app, init_basic_database

if __name__ == '__main__':
    # Initialize database on startup
    init_basic_database()
    
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)