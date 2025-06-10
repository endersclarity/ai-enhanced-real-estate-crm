#!/bin/bash
# Quick health check and common fixes

echo "🏥 Health Check & Auto-Fix"
echo "=========================="

# Function to check and fix database
fix_database() {
    echo "🔧 Checking database..."
    
    # Check if database file exists
    if [ ! -f "real_estate_crm.db" ]; then
        echo "❌ Database missing! Creating..."
        touch real_estate_crm.db
    fi
    
    # Initialize database schema
    echo "📊 Initializing database schema..."
    docker-compose -f docker-compose.dev.yml exec -T app python -c "
import sys
sys.path.append('/app')
from core_app.init_database import init_database, insert_sample_data
print('Initializing database...')
if init_database():
    print('✅ Database initialized')
    if insert_sample_data():
        print('✅ Sample data inserted')
    else:
        print('⚠️  Sample data insertion had issues')
else:
    print('❌ Database initialization failed')
"
}

# Function to test specific endpoints
test_endpoint() {
    local endpoint=$1
    local name=$2
    
    echo -n "Testing $name... "
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000$endpoint)
    
    if [ "$response" = "200" ]; then
        echo "✅ OK"
    else
        echo "❌ Failed (HTTP $response)"
        return 1
    fi
}

# Main checks
echo -e "\n1️⃣ Container Status:"
docker-compose -f docker-compose.dev.yml ps

echo -e "\n2️⃣ Endpoint Tests:"
test_endpoint "/" "Homepage"
test_endpoint "/api/crpa/transactions" "API Transactions"
test_endpoint "/crpa_dashboard" "CRPA Dashboard"

# If clients endpoint fails, try to fix database
if ! test_endpoint "/clients" "Clients Page"; then
    echo -e "\n🔧 Attempting database fix..."
    fix_database
    
    # Restart container
    echo -e "\n🔄 Restarting container..."
    docker-compose -f docker-compose.dev.yml restart app
    sleep 5
    
    # Re-test
    echo -e "\n🔍 Re-testing after fix..."
    test_endpoint "/clients" "Clients Page (after fix)"
fi

echo -e "\n✅ Health check complete!"