#!/usr/bin/env python3
"""
Flask Real Estate CRM Application Entry Point
Integrates the enhanced Flask application with Docker deployment
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app

def main():
    """Main entry point for the Flask CRM application"""
    
    # Create Flask application
    app = create_app()
    
    # Configuration for different environments
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    
    print("🏠 Starting Enhanced Real Estate CRM...")
    print(f"🌐 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📡 Host: {host}:{port}")
    print(f"📝 Navigate to: http://localhost:{port}")
    print(f"💻 Dashboard: http://localhost:{port}")
    print(f"👥 Client Management: http://localhost:{port}/crm/clients")
    print(f"🏘️ Property Management: http://localhost:{port}/crm/properties")
    print(f"🤖 AI Chatbot: http://localhost:{port}/crm/dashboard")
    
    # Run the application
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug,
        threaded=True
    )

if __name__ == '__main__':
    main()
