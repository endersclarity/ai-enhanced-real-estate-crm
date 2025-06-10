#!/bin/bash
# Three-Tier Diagnostic System for Offer Creator (Ported from FitForge)
# TIER 1: Fast-fail diagnostics -> TIER 2: AI analysis -> TIER 3: Human review

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🚀 THREE-TIER DIAGNOSTIC SYSTEM${NC}"
echo -e "${CYAN}================================${NC}"
echo -e "${BLUE}Ported from FitForge's proven architecture${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found!${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found! (needed for AI analyzer)${NC}"
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites met${NC}"
echo ""

# TIER 1: Fast-Fail Diagnostics
echo -e "${MAGENTA}🔥 TIER 1: Fast-Fail Diagnostics${NC}"
echo -e "${MAGENTA}==================================${NC}"

# Ensure container is running
if ! docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Starting Offer Creator container...${NC}"
    docker-compose -f docker-compose.dev.yml up -d
    echo -e "${YELLOW}⏳ Waiting for startup...${NC}"
    sleep 8
fi

# Run fast diagnostics
echo -e "${CYAN}Running fast-fail diagnostics...${NC}"
if ./scripts/simple-check.sh; then
    echo -e "${GREEN}✅ TIER 1 PASSED: System is operational!${NC}"
    echo -e "${GREEN}No AI analysis needed - everything works!${NC}"
    exit 0
else
    DIAGNOSTIC_EXIT_CODE=$?
    echo -e "${RED}❌ TIER 1 FAILED: Issues detected${NC}"
fi

echo ""

# TIER 2: AI Analysis (only runs if Tier 1 fails)
echo -e "${MAGENTA}🧠 TIER 2: AI Analysis${NC}"
echo -e "${MAGENTA}======================${NC}"

# Capture current Docker logs
TIMESTAMP=$(date +%s)
DOCKER_LOG_FILE="docker-logs-${TIMESTAMP}.log"
echo -e "${CYAN}📋 Capturing Docker logs...${NC}"
docker-compose -f docker-compose.dev.yml logs --tail=50 > "$DOCKER_LOG_FILE"

# Find the most recent diagnostic failure log
DIAGNOSTIC_LOG=$(ls -t diagnostic-failure-*.log 2>/dev/null | head -1)

if [ -z "$DIAGNOSTIC_LOG" ]; then
    echo -e "${YELLOW}⚠️  No diagnostic failure log found, creating one...${NC}"
    DIAGNOSTIC_LOG="diagnostic-failure-${TIMESTAMP}.log"
    echo "Fast-fail diagnostic failed with exit code: $DIAGNOSTIC_EXIT_CODE" > "$DIAGNOSTIC_LOG"
    echo "No specific failure log captured." >> "$DIAGNOSTIC_LOG"
fi

echo -e "${CYAN}Using diagnostic log: $DIAGNOSTIC_LOG${NC}"
echo -e "${CYAN}Using docker log: $DOCKER_LOG_FILE${NC}"

# Generate AI analysis prompt
echo -e "${CYAN}🔮 Generating AI analysis prompt...${NC}"
if node scripts/local-ai-analyzer.js "$DIAGNOSTIC_LOG" "$DOCKER_LOG_FILE"; then
    echo ""
    echo -e "${MAGENTA}🎯 TIER 2 COMPLETE: AI prompt generated${NC}"
else
    echo -e "${RED}❌ TIER 2 FAILED: Could not generate AI prompt${NC}"
    exit 1
fi

echo ""

# TIER 3: Human Review Instructions
echo -e "${MAGENTA}👤 TIER 3: Human Review${NC}"
echo -e "${MAGENTA}======================${NC}"
echo -e "${YELLOW}The AI analysis prompt has been generated above.${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo -e "${BLUE}1. Copy the generated prompt${NC}"
echo -e "${BLUE}2. Paste it into Claude Code${NC}"
echo -e "${BLUE}3. Review Claude's analysis and suggested fixes${NC}"
echo -e "${BLUE}4. Apply approved fixes manually${NC}"
echo -e "${BLUE}5. Re-run this script to verify fixes${NC}"
echo ""
echo -e "${GREEN}Files created:${NC}"
echo -e "${GREEN}  - Diagnostic log: $DIAGNOSTIC_LOG${NC}"
echo -e "${GREEN}  - Docker log: $DOCKER_LOG_FILE${NC}"
echo ""
echo -e "${CYAN}To re-run diagnostics after fixes:${NC}"
echo -e "${CYAN}  ./scripts/three-tier-diagnostics.sh${NC}"
