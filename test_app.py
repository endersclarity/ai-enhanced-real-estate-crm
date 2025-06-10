#!/usr/bin/env python3
"""
Simple test script to debug Flask app startup
"""
import sys
import traceback

try:
    print("Testing imports...")
    from app import create_app
    print("✅ App module imported successfully")
    
    print("Creating app...")
    app = create_app()
    print("✅ App created successfully")
    
    print("Starting app...")
    app.run(host='0.0.0.0', port=5000, debug=True)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
