#!/bin/bash
# Restore full functionality to dev instance

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🔧 RESTORING FULL CRM FUNCTIONALITY${NC}"
echo -e "${CYAN}===================================${NC}"

# Step 1: Copy required files to dev container
echo -e "${YELLOW}Step 1: Ensuring all files are in dev container...${NC}"
docker cp populate_rich_crm_data.py offer-creator-dev:/app/
docker cp Listing.csv offer-creator-dev:/app/
docker cp professional_form_filler.py offer-creator-dev:/app/

# Step 2: Restart dev with original CRM
echo -e "${YELLOW}Step 2: Restarting dev with original CRM app...${NC}"
docker-compose -f docker-compose.two-stage.yml restart dev
sleep 10

# Step 3: Initialize database schema
echo -e "${YELLOW}Step 3: Initializing database schema...${NC}"
docker-compose -f docker-compose.two-stage.yml exec -T dev python3 -c "
import sys
sys.path.append('/app/core_app')
try:
    from database_config import db
    db.init_database_schema()
    print('✅ Database schema initialized')
except:
    # Fallback to SQLite initialization
    import sqlite3
    conn = sqlite3.connect('/app/dev_crm.db')
    # Create tables based on original schema
    with open('/app/core_app/database/real_estate_crm_schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()
    print('✅ SQLite database initialized')
"

# Step 4: Populate with rich data
echo -e "${YELLOW}Step 4: Populating database with rich data...${NC}"
docker-compose -f docker-compose.two-stage.yml exec -T dev python3 populate_rich_crm_data.py

# Step 5: Test functionality
echo -e "${YELLOW}Step 5: Testing restored functionality...${NC}"

# Test endpoints
endpoints=(
    "/"
    "/clients"
    "/properties"
    "/transactions"
    "/debug_chat"
    "/crpa_dashboard"
    "/api/dashboard_stats"
)

echo -e "${BLUE}Testing endpoints...${NC}"
for endpoint in "${endpoints[@]}"; do
    response=$(docker-compose -f docker-compose.two-stage.yml exec -T dev curl -s -o /dev/null -w "%{http_code}" http://localhost:5000$endpoint)
    if [ "$response" = "200" ] || [ "$response" = "302" ]; then
        echo -e "  $endpoint: ${GREEN}✅ $response${NC}"
    else
        echo -e "  $endpoint: ${RED}❌ $response${NC}"
    fi
done

# Show database stats
echo -e "\n${BLUE}Database Statistics:${NC}"
docker-compose -f docker-compose.two-stage.yml exec -T dev python3 -c "
import sqlite3
conn = sqlite3.connect('/app/dev_crm.db')
try:
    clients = conn.execute('SELECT COUNT(*) FROM clients').fetchone()[0]
    properties = conn.execute('SELECT COUNT(*) FROM properties').fetchone()[0]
    transactions = conn.execute('SELECT COUNT(*) FROM transactions').fetchone()[0]
    print(f'  Clients: {clients}')
    print(f'  Properties: {properties}')
    print(f'  Transactions: {transactions}')
except Exception as e:
    print(f'  Error reading stats: {e}')
conn.close()
"

# Show access URLs
WSL_IP=$(ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d/ -f1)
echo -e "\n${GREEN}✨ FULL CRM RESTORED!${NC}"
echo -e "${CYAN}Access the complete system at:${NC}"
echo -e "  Dashboard: ${GREEN}http://$WSL_IP:5001/${NC}"
echo -e "  AI Chat: ${GREEN}http://$WSL_IP:5001/debug_chat${NC}"
echo -e "  CRPA Forms: ${GREEN}http://$WSL_IP:5001/crpa_dashboard${NC}"
echo -e "  Clients: ${GREEN}http://$WSL_IP:5001/clients${NC}"
echo -e "  Properties: ${GREEN}http://$WSL_IP:5001/properties${NC}"