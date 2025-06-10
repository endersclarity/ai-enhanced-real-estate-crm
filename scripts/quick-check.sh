#!/bin/bash
# Quick validation script for three-tier setup

echo "🔍 Real Estate CRM - Quick Environment Check"
echo "==========================================="

# Check Python project files
echo -e "\n1️⃣ Checking Python project structure..."
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt found"
else
    echo "❌ requirements.txt missing"
fi

if [ -f "core_app/real_estate_crm.py" ]; then
    echo "✅ Main Flask app found"
else
    echo "❌ core_app/real_estate_crm.py missing"
fi

# Check Docker files
echo -e "\n2️⃣ Checking Docker setup..."
if [ -f "docker-compose.dev.yml" ]; then
    echo "✅ docker-compose.dev.yml found"
else
    echo "❌ docker-compose.dev.yml missing"
fi

if [ -f "docker/Dockerfile.dev" ]; then
    echo "✅ Dockerfile.dev found"
else
    echo "❌ docker/Dockerfile.dev missing"
fi

# Check database
echo -e "\n3️⃣ Checking database..."
if [ -f "real_estate_crm.db" ]; then
    DB_SIZE=$(ls -lh real_estate_crm.db | awk '{print $5}')
    echo "✅ Database found (size: $DB_SIZE)"
else
    echo "⚠️  Database not found (will be created on first run)"
fi

# Check environment
echo -e "\n4️⃣ Checking environment variables..."
if [ -f ".env" ]; then
    echo "✅ .env file found"
    if grep -q "GEMINI_API_KEY" .env; then
        echo "✅ GEMINI_API_KEY configured"
    else
        echo "❌ GEMINI_API_KEY missing in .env"
    fi
else
    echo "⚠️  .env file not found (will be created by start-dev.sh)"
fi

# Check Docker daemon
echo -e "\n5️⃣ Checking Docker..."
if docker info > /dev/null 2>&1; then
    echo "✅ Docker is running"
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | sed 's/,$//')
    echo "   Version: $DOCKER_VERSION"
else
    echo "❌ Docker is not running or not installed"
fi

# Summary
echo -e "\n📊 Summary"
echo "=========="
if [ -f "requirements.txt" ] && [ -f "core_app/real_estate_crm.py" ] && [ -f "docker-compose.dev.yml" ]; then
    echo "✅ Ready to start development environment"
    echo "   Run: ./scripts/start-dev.sh"
else
    echo "❌ Missing required files. Please check the setup."
fi