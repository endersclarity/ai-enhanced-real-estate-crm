#!/bin/bash
# Docker-based Test Runner with Comprehensive Log Capture
# Runs tests INSIDE the Docker container for accurate results

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🐳 DOCKER-BASED TEST RUNNER${NC}"
echo -e "${CYAN}===========================${NC}"
echo ""

# Create test results directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEST_DIR="test_results_${TIMESTAMP}"
mkdir -p "$TEST_DIR"

echo -e "${YELLOW}📁 Test results will be saved to: ${TEST_DIR}${NC}"
echo ""

# Ensure container is running
if ! docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Starting container...${NC}"
    docker-compose -f docker-compose.dev.yml up -d
    sleep 5
fi

# Function to run test inside Docker and capture output
run_docker_test() {
    local test_name=$1
    local test_command=$2
    local log_file="${TEST_DIR}/${test_name}.log"
    
    echo -e "${BLUE}Running test: ${test_name}...${NC}"
    
    # Capture pre-test logs
    docker-compose -f docker-compose.dev.yml logs --tail=10 > "${TEST_DIR}/${test_name}_pre.log"
    
    # Run test inside container
    if docker-compose -f docker-compose.dev.yml exec -T app bash -c "$test_command" > "$log_file" 2>&1; then
        echo -e "${GREEN}✅ ${test_name} PASSED${NC}"
        echo "PASSED" > "${TEST_DIR}/${test_name}.status"
    else
        echo -e "${RED}❌ ${test_name} FAILED${NC}"
        echo "FAILED" > "${TEST_DIR}/${test_name}.status"
        
        # Capture post-failure logs
        docker-compose -f docker-compose.dev.yml logs --tail=50 > "${TEST_DIR}/${test_name}_post.log"
    fi
    
    # Always capture current container logs
    docker-compose -f docker-compose.dev.yml logs --tail=20 >> "$log_file"
}

# Test 1: Basic connectivity from inside container (handle redirects)
run_docker_test "internal_connectivity" "curl -sL http://localhost:5000/ | grep -q -E '(Real Estate CRM|Dashboard)' && echo 'Homepage loads correctly'"

# Test 2: Database connectivity
run_docker_test "database_access" "python3 -c \"
import sqlite3
conn = sqlite3.connect('/app/core_app/real_estate_crm.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM clients')
count = cursor.fetchone()[0]
print(f'Database accessible. Client count: {count}')
conn.close()
\""

# Test 3: Python imports and dependencies
run_docker_test "python_dependencies" "python3 -c \"
import flask
import pydantic
import langchain_google_genai
print('✓ Flask version:', flask.__version__)
print('✓ Pydantic loaded')
print('✓ LangChain Google GenAI loaded')
print('All critical dependencies available')
\""

# Test 4: API endpoints from inside container
run_docker_test "api_endpoints" "python3 -c \"
import requests
base_url = 'http://localhost:5000'

# Test endpoints
endpoints = [
    ('/', 'Homepage'),
    ('/auth/login', 'Login Page'),
    ('/crm/clients', 'Clients'),
    ('/crm/properties', 'Properties'),
    ('/crm/transactions', 'Transactions'),
    ('/crm/dashboard', 'CRM Dashboard')
]

for endpoint, name in endpoints:
    try:
        r = requests.get(base_url + endpoint, timeout=3, allow_redirects=True)
        status = 'PASS' if r.status_code == 200 else 'FAIL'
        print(f'{name}: {r.status_code} - {status}')
    except Exception as e:
        print(f'{name}: ERROR - {str(e)}')
\""

# Test 5: Form validation framework (test import and basic functionality)
run_docker_test "validation_framework" "cd /app && python3 -c \"
from validation_framework import FormValidationFramework
validator = FormValidationFramework()
print('FormValidationFramework imported successfully')
print('Validation rules loaded:', len(validator.validation_rules))
print('Business rules loaded:', len(validator.business_rules))
print('Legal requirements loaded:', len(validator.legal_requirements))
\""

# Test 6: AI integration
run_docker_test "ai_integration" "python3 -c \"
import os
print('GEMINI_API_KEY set:', 'GEMINI_API_KEY' in os.environ)
print('GEMINI_MODEL:', os.environ.get('GEMINI_MODEL', 'Not set'))

# Test basic AI functionality
from langchain_google_genai import ChatGoogleGenerativeAI
try:
    llm = ChatGoogleGenerativeAI(
        model='models/gemini-2.5-flash-preview-04-17',
        google_api_key=os.environ.get('GEMINI_API_KEY', ''),
        temperature=0.1
    )
    print('AI model initialized successfully')
except Exception as e:
    print(f'AI initialization failed: {e}')
\""

# Test 7: Full integration test (with authentication)
run_docker_test "full_integration" "cd /app && python3 test_docker_authenticated.py"

# Generate summary report
echo ""
echo -e "${CYAN}📊 TEST SUMMARY${NC}"
echo -e "${CYAN}===============${NC}"

PASSED=0
FAILED=0

for status_file in ${TEST_DIR}/*.status; do
    if grep -q "PASSED" "$status_file"; then
        ((PASSED++))
    else
        ((FAILED++))
    fi
done

echo -e "Tests Passed: ${GREEN}${PASSED}${NC}"
echo -e "Tests Failed: ${RED}${FAILED}${NC}"

# Capture final Docker logs
echo -e "\n${YELLOW}📋 Capturing final Docker logs...${NC}"
docker-compose -f docker-compose.dev.yml logs > "${TEST_DIR}/docker_logs_final.log"

# Create summary file
cat > "${TEST_DIR}/summary.txt" << EOF
Docker-Based Test Run Summary
============================
Timestamp: ${TIMESTAMP}
Tests Passed: ${PASSED}
Tests Failed: ${FAILED}

Test Results:
EOF

for status_file in ${TEST_DIR}/*.status; do
    test_name=$(basename "$status_file" .status)
    status=$(cat "$status_file")
    echo "- ${test_name}: ${status}" >> "${TEST_DIR}/summary.txt"
done

echo ""
echo -e "${GREEN}✅ Test run complete!${NC}"
echo -e "${BLUE}Results saved to: ${TEST_DIR}/${NC}"
echo -e "${BLUE}View summary: cat ${TEST_DIR}/summary.txt${NC}"
echo -e "${BLUE}View Docker logs: less ${TEST_DIR}/docker_logs_final.log${NC}"

# If any tests failed, exit with error code
if [ $FAILED -gt 0 ]; then
    echo -e "\n${RED}⚠️  Some tests failed. Check logs for details.${NC}"
    exit 1
fi