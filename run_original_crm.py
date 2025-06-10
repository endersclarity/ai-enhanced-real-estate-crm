#!/usr/bin/env python3
"""
Run the ORIGINAL feature-rich Real Estate CRM
This loads the complete system with AI, forms, and MLS integration
"""

import os
import sys

# Add core_app to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core_app'))

# Import and run the original CRM
from real_estate_crm import app

if __name__ == '__main__':
    # Get configuration
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    
    print("🏠 Starting ORIGINAL Real Estate CRM with FULL features...")
    print(f"🌐 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📡 Host: {host}:{port}")
    print(f"✨ Features: AI Chatbot, Form Generation, MLS Integration")
    print(f"📊 Dashboard: http://localhost:{port}")
    print(f"💬 AI Chat: http://localhost:{port}/debug_chat")
    print(f"📋 CRPA Forms: http://localhost:{port}/crpa_dashboard")
    print(f"👥 Clients: http://localhost:{port}/clients")
    print(f"🏘️ Properties: http://localhost:{port}/properties")
    
    # Initialize database if needed
    try:
        from database_config import db
        db.init_database_schema()
        print("✅ Database schema initialized")
    except Exception as e:
        print(f"⚠️  Database initialization skipped: {e}")
    
    # Run the app
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug,
        threaded=True
    )