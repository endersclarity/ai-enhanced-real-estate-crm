#!/bin/bash
# Production startup script for Real Estate CRM with Supabase
# Task 5 - Complete Supabase Integration

echo "🏠 Real Estate CRM - Production Startup with Supabase"
echo "=================================================="

# Load environment variables from supabase_config.env
if [ -f "supabase_config.env" ]; then
    echo "📋 Loading Supabase configuration..."
    set -a  # automatically export all variables
    source supabase_config.env
    set +a
    echo "✅ Supabase environment loaded"
else
    echo "⚠️  supabase_config.env not found, using default configuration"
fi

# Set production environment
export USE_SUPABASE=true
export FLASK_ENV=production
export GEMINI_API_KEY="AIzaSyCJ8-hQJVLGXDkHy2sjw-O6Dls0FVO0gGU"

# Get WSL IP for Windows browser access
WSL_IP=$(ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d/ -f1)
PORT=${PORT:-8080}

echo "🌐 Server will be accessible at:"
echo "   Local:   http://localhost:$PORT"
echo "   Windows: http://$WSL_IP:$PORT"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  Virtual environment not found, running with system Python"
fi

# Test database connection
echo "🔌 Testing Supabase connection..."
python3 -c "
from database_config import db
success = db.init_database_schema()
if success:
    print('✅ Supabase PostgreSQL connection verified')
    summary = db.get_clients_summary()
    print(f'   📊 Database ready: {summary[\"total_clients\"]} clients')
else:
    print('❌ Database connection failed')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Starting Flask application with Supabase..."
    echo "   Press Ctrl+C to stop the server"
    echo ""
    
    # Start the application
    python3 app.py
else
    echo "❌ Database connection test failed. Check your Supabase configuration."
    exit 1
fi