#!/bin/bash
# Two-Stage Docker Management Script
# Simple commands for dev → staging → deployment workflow

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Function to show usage
show_usage() {
    echo -e "${CYAN}Two-Stage Docker Manager${NC}"
    echo -e "${CYAN}========================${NC}"
    echo ""
    echo "Commands:"
    echo "  ./two-stage-manager.sh start         - Start both instances"
    echo "  ./two-stage-manager.sh start-dev     - Start only dev instance"
    echo "  ./two-stage-manager.sh start-staging - Start only staging instance"
    echo "  ./two-stage-manager.sh stop          - Stop all instances"
    echo "  ./two-stage-manager.sh status        - Show instance status"
    echo "  ./two-stage-manager.sh test-dev      - Run tests on dev instance"
    echo "  ./two-stage-manager.sh test-staging  - Run tests on staging instance"
    echo "  ./two-stage-manager.sh promote       - Promote dev to staging"
    echo "  ./two-stage-manager.sh logs-dev      - Show dev instance logs"
    echo "  ./two-stage-manager.sh logs-staging  - Show staging logs"
    echo "  ./two-stage-manager.sh shell-dev     - Get shell in dev container"
    echo "  ./two-stage-manager.sh shell-staging - Get shell in staging container"
    echo "  ./two-stage-manager.sh urls          - Show access URLs"
}

# Function to get WSL IP
get_wsl_ip() {
    WSL_IP=$(ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d/ -f1)
    echo $WSL_IP
}

# Start both instances
start_all() {
    echo -e "${YELLOW}Starting both instances...${NC}"
    docker-compose -f docker-compose.two-stage.yml up -d
    sleep 3
    show_urls
}

# Start specific instance
start_instance() {
    local instance=$1
    echo -e "${YELLOW}Starting $instance instance...${NC}"
    docker-compose -f docker-compose.two-stage.yml up -d $instance
    sleep 3
    show_urls
}

# Stop all instances
stop_all() {
    echo -e "${YELLOW}Stopping all instances...${NC}"
    docker-compose -f docker-compose.two-stage.yml down
}

# Show status
show_status() {
    echo -e "${CYAN}Instance Status:${NC}"
    docker-compose -f docker-compose.two-stage.yml ps
}

# Run tests on specific instance
run_tests() {
    local instance=$1
    local port=$2
    
    echo -e "${CYAN}Running tests on $instance instance (port $port)...${NC}"
    
    # Create temporary test script
    cat > /tmp/test_instance.sh << 'EOF'
#!/bin/bash
PORT=$1
echo "Testing instance on port $PORT..."

# Basic connectivity
echo -n "1. Basic connectivity: "
if curl -s http://localhost:$PORT/ > /dev/null; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
    exit 1
fi

# Check endpoints
echo -n "2. Login page: "
if curl -s http://localhost:$PORT/auth/login | grep -q "login"; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
fi

# Check database
echo -n "3. CRM endpoints: "
if curl -s http://localhost:$PORT/crm/dashboard > /dev/null; then
    echo "✅ PASS"
else
    echo "⚠️  Requires auth (expected)"
fi

echo "Basic tests complete!"
EOF
    
    chmod +x /tmp/test_instance.sh
    # Copy script to container and execute
    docker cp /tmp/test_instance.sh offer-creator-$instance:/tmp/
    docker-compose -f docker-compose.two-stage.yml exec -T $instance bash /tmp/test_instance.sh $port
    docker-compose -f docker-compose.two-stage.yml exec -T $instance rm /tmp/test_instance.sh
    rm /tmp/test_instance.sh
}

# Promote dev to staging
promote_to_staging() {
    echo -e "${CYAN}Promoting dev → staging${NC}"
    echo -e "${YELLOW}This will copy the current dev state to staging${NC}"
    
    # Run tests on dev first
    echo -e "\n${BLUE}Step 1: Testing dev instance...${NC}"
    if ! run_tests "dev" "5000"; then
        echo -e "${RED}❌ Dev tests failed! Fix issues before promoting.${NC}"
        exit 1
    fi
    
    echo -e "\n${BLUE}Step 2: Creating snapshot of dev...${NC}"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    
    # Stop staging
    docker-compose -f docker-compose.two-stage.yml stop staging
    
    # Copy dev database to staging
    echo -e "${BLUE}Step 3: Copying database...${NC}"
    docker-compose -f docker-compose.two-stage.yml exec -T dev cp /app/dev_crm.db /tmp/staging_snapshot.db
    docker cp offer-creator-dev:/tmp/staging_snapshot.db ./staging_snapshot_${TIMESTAMP}.db
    
    # Rebuild staging with latest code
    echo -e "${BLUE}Step 4: Rebuilding staging...${NC}"
    docker-compose -f docker-compose.two-stage.yml build staging
    
    # Start staging
    docker-compose -f docker-compose.two-stage.yml up -d staging
    sleep 5
    
    # Copy database to staging
    docker cp ./staging_snapshot_${TIMESTAMP}.db offer-creator-staging:/app/data/staging_crm.db
    docker-compose -f docker-compose.two-stage.yml exec -T staging chown 1000:1000 /app/data/staging_crm.db
    
    echo -e "\n${BLUE}Step 5: Testing staging instance...${NC}"
    if run_tests "staging" "5000"; then
        echo -e "\n${GREEN}✅ Promotion successful!${NC}"
        echo -e "${GREEN}Staging is now running the promoted code at http://$(get_wsl_ip):5002${NC}"
    else
        echo -e "\n${RED}⚠️  Staging tests failed, but promotion completed${NC}"
    fi
}

# Show logs
show_logs() {
    local instance=$1
    docker-compose -f docker-compose.two-stage.yml logs -f --tail=50 $instance
}

# Get shell
get_shell() {
    local instance=$1
    docker-compose -f docker-compose.two-stage.yml exec $instance /bin/bash
}

# Show URLs
show_urls() {
    local WSL_IP=$(get_wsl_ip)
    echo -e "\n${CYAN}Access URLs:${NC}"
    echo -e "${GREEN}Dev Instance:     http://$WSL_IP:5001${NC} (for fucking around)"
    echo -e "${BLUE}Staging Instance: http://$WSL_IP:5002${NC} (clean, ready to deploy)"
    echo ""
}

# Main command handling
case "$1" in
    start)
        start_all
        ;;
    start-dev)
        start_instance "dev"
        ;;
    start-staging)
        start_instance "staging"
        ;;
    stop)
        stop_all
        ;;
    status)
        show_status
        ;;
    test-dev)
        run_tests "dev" "5000"
        ;;
    test-staging)
        run_tests "staging" "5000"
        ;;
    promote)
        promote_to_staging
        ;;
    logs-dev)
        show_logs "dev"
        ;;
    logs-staging)
        show_logs "staging"
        ;;
    shell-dev)
        get_shell "dev"
        ;;
    shell-staging)
        get_shell "staging"
        ;;
    urls)
        show_urls
        ;;
    *)
        show_usage
        ;;
esac