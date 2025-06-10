#!/bin/bash
# Test runner for two-stage Docker environment
# Runs tests against dev or staging instances

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

INSTANCE=${1:-dev}
PORT=$([[ "$INSTANCE" == "staging" ]] && echo "5002" || echo "5001")

echo -e "${CYAN}🐳 TWO-STAGE TEST RUNNER (${INSTANCE})${NC}"
echo -e "${CYAN}====================================${NC}"
echo ""

# Create test results directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEST_DIR="test_results_${INSTANCE}_${TIMESTAMP}"
mkdir -p "$TEST_DIR"

echo -e "${YELLOW}📁 Test results will be saved to: ${TEST_DIR}${NC}"
echo ""

# Ensure container is running
if ! docker-compose -f docker-compose.two-stage.yml ps | grep -q "offer-creator-${INSTANCE}.*Up"; then
    echo -e "${YELLOW}⚠️  Starting ${INSTANCE} container...${NC}"
    docker-compose -f docker-compose.two-stage.yml up -d $INSTANCE
    sleep 5
fi

# Function to run test and capture output
run_test() {
    local test_name=$1
    local test_command=$2
    local log_file="${TEST_DIR}/${test_name}.log"
    
    echo -e "${BLUE}Running test: ${test_name}...${NC}"
    
    # Run test
    if eval "$test_command" > "$log_file" 2>&1; then
        echo -e "${GREEN}✅ ${test_name} PASSED${NC}"
        echo "PASSED" > "${TEST_DIR}/${test_name}.status"
        return 0
    else
        echo -e "${RED}❌ ${test_name} FAILED${NC}"
        echo "FAILED" > "${TEST_DIR}/${test_name}.status"
        return 1
    fi
}

# Test 1: Basic connectivity
run_test "connectivity" "curl -sL http://localhost:${PORT}/ -o /dev/null -w '%{http_code}' | grep -E '200|302'"

# Test 2: CRM endpoints
endpoints=(
    "/" "dashboard"
    "/clients" "clients"
    "/properties" "properties"
    "/transactions" "transactions"
    "/debug_chat" "ai_chat"
    "/crpa_dashboard" "crpa_forms"
    "/api/dashboard_stats" "api_stats"
)

for ((i=0; i<${#endpoints[@]}; i+=2)); do
    endpoint="${endpoints[i]}"
    name="${endpoints[i+1]}"
    run_test "endpoint_${name}" "curl -s -o /dev/null -w '%{http_code}' http://localhost:${PORT}${endpoint} | grep -E '200|302'"
done

# Test 3: Database check
run_test "database" "docker-compose -f docker-compose.two-stage.yml exec -T ${INSTANCE} python3 -c \"
import sqlite3
conn = sqlite3.connect('/app/real_estate_crm.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM clients')
clients = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM properties')
properties = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM transactions')
transactions = cursor.fetchone()[0]
print(f'Clients: {clients}, Properties: {properties}, Transactions: {transactions}')
assert clients > 0 and properties > 0 and transactions > 0
conn.close()
\""

# Test 4: Schema validation
run_test "schema" "docker-compose -f docker-compose.two-stage.yml exec -T ${INSTANCE} python3 -c \"
import sqlite3
conn = sqlite3.connect('/app/real_estate_crm.db')
cursor = conn.cursor()

# Check properties table
cursor.execute('PRAGMA table_info(properties)')
prop_cols = [col[1] for col in cursor.fetchall()]
required_cols = ['street_address', 'listed_price', 'zillow_url', 'realtor_url', 'mls_portal_url']
missing = [col for col in required_cols if col not in prop_cols]
assert not missing, f'Missing property columns: {missing}'

# Check transactions table
cursor.execute('PRAGMA table_info(transactions)')
trans_cols = [col[1] for col in cursor.fetchall()]
required_cols = ['buyer_client_id', 'seller_client_id', 'close_of_escrow_date']
missing = [col for col in required_cols if col not in trans_cols]
assert not missing, f'Missing transaction columns: {missing}'

print('Schema validation passed')
conn.close()
\""

# Test 5: AI Configuration
run_test "ai_config" "docker-compose -f docker-compose.two-stage.yml exec -T ${INSTANCE} python3 -c \"
import os
assert 'GEMINI_API_KEY' in os.environ, 'GEMINI_API_KEY not set'
print(f'AI configured with model: {os.environ.get(\\\"GEMINI_MODEL\\\", \\\"default\\\")}')
\""

# Generate summary report
echo ""
echo -e "${CYAN}📊 TEST SUMMARY${NC}"
echo -e "${CYAN}===============${NC}"

PASSED=0
FAILED=0

for status_file in ${TEST_DIR}/*.status; do
    if [ -f "$status_file" ]; then
        if grep -q "PASSED" "$status_file"; then
            ((PASSED++))
        else
            ((FAILED++))
        fi
    fi
done

echo "Tests Passed: ${PASSED}"
echo "Tests Failed: ${FAILED}"

# Calculate confidence score
TOTAL=$((PASSED + FAILED))
if [ $TOTAL -gt 0 ]; then
    CONFIDENCE=$(echo "scale=2; $PASSED / $TOTAL" | bc)
else
    CONFIDENCE=0
fi

echo "Confidence Score: ${CONFIDENCE}"

# Create summary file
cat > "${TEST_DIR}/summary.json" << EOF
{
  "instance": "${INSTANCE}",
  "timestamp": "${TIMESTAMP}",
  "tests_passed": ${PASSED},
  "tests_failed": ${FAILED},
  "confidence_score": ${CONFIDENCE},
  "ready_for_promotion": $([ "$CONFIDENCE" == "1.00" ] && echo "true" || echo "false")
}
EOF

echo ""
echo -e "${GREEN}✅ Test run complete!${NC}"
echo -e "${BLUE}Results saved to: ${TEST_DIR}/${NC}"

# Return appropriate exit code
if [ "$CONFIDENCE" == "1.00" ]; then
    exit 0
else
    exit 1
fi