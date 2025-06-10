#!/bin/bash
# Simple fast-fail diagnostics using curl only
# No Python dependencies

# Removed set -euo pipefail for debugging

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🚀 SIMPLE HEALTH CHECK${NC}"
echo -e "${CYAN}=====================${NC}"

BASE_URL="http://localhost:5000"
TIMEOUT=5

test_endpoint() {
    local name="$1"
    local url="$2"
    
    echo -n "Testing $name... "
    
    status=$(curl -o /dev/null -s -w "%{http_code}" --max-time $TIMEOUT "$url" 2>/dev/null || echo "000")
    
    # Accept 200 (OK) and 302 (authentication redirect) as success
    if [ "$status" = "200" ] || [ "$status" = "302" ]; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED (HTTP $status)${NC}"
        return 1
    fi
}

# Test all endpoints
ALL_PASSED=true

test_endpoint "Homepage" "$BASE_URL/" || ALL_PASSED=false
test_endpoint "Clients" "$BASE_URL/crm/clients" || ALL_PASSED=false
test_endpoint "Properties" "$BASE_URL/crm/properties" || ALL_PASSED=false
test_endpoint "Dashboard" "$BASE_URL/crm/dashboard" || ALL_PASSED=false

if [ "$ALL_PASSED" = true ]; then
    echo -e "\n${GREEN}🎉 ALL CHECKS PASSED!${NC}"
    echo -e "${GREEN}✅ Real Estate CRM is operational${NC}"
    exit 0
else
    echo -e "\n${RED}❌ SOME CHECKS FAILED${NC}"
    echo -e "${YELLOW}Check Docker logs for details:${NC}"
    echo -e "${CYAN}docker-compose -f docker-compose.dev.yml logs --tail=20${NC}"
    exit 1
fi
