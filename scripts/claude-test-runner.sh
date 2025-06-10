#!/bin/bash
# Claude Code Test Runner - Simple interface for autonomous testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🤖 CLAUDE CODE AUTONOMOUS TEST RUNNER${NC}"
echo -e "${CYAN}=====================================${NC}"

# Function to run autonomous testing
run_autonomous_test() {
    local instance=$1
    echo -e "${BLUE}Running autonomous testing on ${instance} instance...${NC}"
    
    python3 scripts/autonomous-orchestrator.py "$instance"
}

# Function to promote between environments
promote_if_ready() {
    echo -e "${YELLOW}Checking if dev is ready for promotion...${NC}"
    
    # Run autonomous test on dev
    result=$(python3 scripts/autonomous-orchestrator.py dev)
    
    if echo "$result" | grep -q '"ready_for_promotion": true'; then
        echo -e "${GREEN}✅ Dev is ready! Promoting to staging...${NC}"
        ./scripts/two-stage-manager.sh promote
        
        echo -e "${YELLOW}Now testing staging environment...${NC}"
        python3 scripts/autonomous-orchestrator.py staging
    else
        echo -e "${RED}❌ Dev not ready for promotion yet${NC}"
        echo "$result" | python3 -m json.tool | grep -A5 persistent_failures || true
    fi
}

# Function to run full pipeline
run_full_pipeline() {
    echo -e "${CYAN}🚀 Running full autonomous pipeline${NC}"
    
    # Test dev until confident
    echo -e "${BLUE}Phase 1: Testing dev environment...${NC}"
    dev_result=$(python3 scripts/autonomous-orchestrator.py dev)
    
    if echo "$dev_result" | grep -q '"status": "SUCCESS"'; then
        echo -e "${GREEN}✅ Dev testing successful!${NC}"
        
        # Promote to staging
        echo -e "${BLUE}Phase 2: Promoting to staging...${NC}"
        ./scripts/two-stage-manager.sh promote
        
        # Test staging until confident
        echo -e "${BLUE}Phase 3: Testing staging environment...${NC}"
        staging_result=$(python3 scripts/autonomous-orchestrator.py staging)
        
        if echo "$staging_result" | grep -q '"status": "SUCCESS"'; then
            echo -e "${GREEN}🎉 FULL PIPELINE SUCCESS!${NC}"
            echo -e "${GREEN}Staging is ready for DigitalOcean deployment${NC}"
            echo -e "${YELLOW}Run: ./scripts/deploy-to-digitalocean.sh${NC}"
        else
            echo -e "${RED}❌ Staging testing failed${NC}"
            echo "$staging_result" | python3 -m json.tool | grep -A5 persistent_failures || true
        fi
    else
        echo -e "${RED}❌ Dev testing failed${NC}"
        echo "$dev_result" | python3 -m json.tool | grep -A5 persistent_failures || true
    fi
}

# Main command handling
case "${1:-help}" in
    "dev")
        run_autonomous_test "dev"
        ;;
    "staging") 
        run_autonomous_test "staging"
        ;;
    "promote")
        promote_if_ready
        ;;
    "pipeline")
        run_full_pipeline
        ;;
    "help"|*)
        echo -e "${YELLOW}Available commands:${NC}"
        echo "  dev      - Run autonomous testing on dev until confident"
        echo "  staging  - Run autonomous testing on staging until confident"
        echo "  promote  - Check dev readiness and promote if confident"
        echo "  pipeline - Run full dev → staging → ready pipeline"
        echo ""
        echo -e "${CYAN}Examples:${NC}"
        echo "  ./scripts/claude-test-runner.sh dev"
        echo "  ./scripts/claude-test-runner.sh pipeline"
        ;;
esac