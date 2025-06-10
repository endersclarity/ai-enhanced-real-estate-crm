#!/bin/bash
# Start development environment with Docker

echo "🚀 Starting Real Estate CRM Development Environment"
echo "=================================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Creating .env file with default values..."
    cat > .env << EOF
GEMINI_API_KEY=AIzaSyCJ8-hQJVLGXDkHy2sjw-O6Dls0FVO0gGU
FLASK_ENV=development
EOF
fi

# Build and start containers
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.dev.yml build

echo "🏃 Starting services..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 5

# Show status
echo "📊 Service Status:"
docker-compose -f docker-compose.dev.yml ps

# Show logs
echo -e "\n📋 Application Logs (last 20 lines):"
docker-compose -f docker-compose.dev.yml logs --tail=20 app

# Get container IP
APP_URL="http://localhost:5000"
echo -e "\n✅ Development environment is running!"
echo "🌐 Access the application at: $APP_URL"
echo "📝 View logs: docker-compose -f docker-compose.dev.yml logs -f app"
echo "🛑 Stop services: docker-compose -f docker-compose.dev.yml down"