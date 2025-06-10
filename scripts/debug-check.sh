#!/bin/bash
# Debug version of health check

echo "Starting debug check..."

BASE_URL="http://localhost:5000"
TIMEOUT=5

echo "Testing homepage..."
status=$(curl -o /dev/null -s -w "%{http_code}" --max-time $TIMEOUT "$BASE_URL/" 2>/dev/null || echo "000")
echo "Homepage status: $status"

if [ "$status" = "200" ]; then
    echo "✅ Homepage OK"
else
    echo "❌ Homepage failed"
fi

echo "Debug check complete."
