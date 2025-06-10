#!/bin/bash
# Run diagnostics against Docker environment

echo "🚀 Running Tier 2 Diagnostics"
echo "============================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker first."
    exit 1
fi

# Check if app container is running
if ! docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
    echo "⚠️  App container not running. Starting it..."
    docker-compose -f docker-compose.dev.yml up -d
    echo "⏳ Waiting for app to start..."
    sleep 5
fi

# Get container status
echo -e "\n📊 Container Status:"
docker-compose -f docker-compose.dev.yml ps

# Run diagnostics from host (testing Docker container)
echo -e "\n🔍 Running diagnostics from host..."
python scripts/diagnostics.py --docker

# Optionally run diagnostics from inside container
echo -e "\n🔍 Running diagnostics from inside container..."
docker-compose -f docker-compose.dev.yml exec app python scripts/diagnostics.py --url http://localhost:5000 --docker

echo -e "\n✅ Diagnostic run complete!"