#!/bin/bash

echo "🏠 Offer Creator - Narissa Realty"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📚 Installing requirements..."
pip install -q -r requirements.txt

# Create output directory
mkdir -p output

# Start the application
echo "🚀 Starting Offer Creator..."
echo ""
python app.py