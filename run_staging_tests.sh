#!/bin/bash
# Run E2E tests against staging instance

echo "🧪 Real Estate CRM - Staging Test Runner"
echo "========================================"

# Check if staging is running
if ! docker ps | grep -q offer-creator-staging; then
    echo "❌ Staging container not running!"
    echo "Starting staging container..."
    docker-compose -f docker-compose.two-stage.yml up -d staging
    echo "Waiting for staging to start..."
    sleep 10
fi

# Install test dependencies if needed
if ! python3 -c "import colorama" 2>/dev/null; then
    echo "📦 Installing test dependencies..."
    pip install colorama requests
fi

# Run the tests
echo ""
echo "🚀 Running E2E tests against staging (http://localhost:5002)"
echo "📝 These tests are READ-ONLY - no data will be modified"
echo ""

python3 test_staging_e2e.py

# Save test results
TEST_EXIT_CODE=$?
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="test_results_staging_${TIMESTAMP}"

mkdir -p $RESULTS_DIR

# Run additional checks
echo ""
echo "📊 Running additional diagnostics..."

# Check response times
echo "Response time check:" > $RESULTS_DIR/performance.txt
for endpoint in "/" "/clients" "/properties" "/transactions"; do
    TIME=$(curl -o /dev/null -s -w "%{time_total}\n" http://localhost:5002$endpoint)
    echo "$endpoint: ${TIME}s" >> $RESULTS_DIR/performance.txt
done

# Check memory usage
docker stats offer-creator-staging --no-stream > $RESULTS_DIR/container_stats.txt

# Summary
echo ""
echo "📁 Test results saved to: $RESULTS_DIR/"
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed! Staging is ready for deployment."
else
    echo "❌ Some tests failed. Please review before deploying."
fi

exit $TEST_EXIT_CODE