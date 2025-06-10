#!/bin/bash
# Test CRM features are working

echo "🧪 Testing CRM Features..."
echo "========================="

# Test endpoints
endpoints=(
    "/" "Dashboard"
    "/clients" "Clients"
    "/properties" "Properties" 
    "/transactions" "Transactions"
    "/debug_chat" "AI Chat"
    "/crpa_dashboard" "CRPA Forms"
    "/api/dashboard_stats" "API Stats"
)

passed=0
failed=0

for ((i=0; i<${#endpoints[@]}; i+=2)); do
    endpoint="${endpoints[i]}"
    name="${endpoints[i+1]}"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001$endpoint)
    
    if [ "$response" = "200" ] || [ "$response" = "302" ]; then
        echo "✅ $name ($endpoint): $response"
        ((passed++))
    else
        echo "❌ $name ($endpoint): $response"
        ((failed++))
    fi
done

echo ""
echo "Summary: $passed passed, $failed failed"

# Test database
echo ""
echo "📊 Database Statistics:"
docker-compose -f docker-compose.two-stage.yml exec -T dev python3 -c "
import sqlite3
conn = sqlite3.connect('/app/dev_crm.db')
clients = conn.execute('SELECT COUNT(*) FROM clients').fetchone()[0]
properties = conn.execute('SELECT COUNT(*) FROM properties').fetchone()[0]
transactions = conn.execute('SELECT COUNT(*) FROM transactions').fetchone()[0]
print(f'  Clients: {clients}')
print(f'  Properties: {properties}')
print(f'  Transactions: {transactions}')
conn.close()
"

# Overall result
if [ $failed -eq 0 ]; then
    echo ""
    echo "✅ All CRM features working!"
    exit 0
else
    echo ""
    echo "⚠️  Some features need attention"
    exit 1
fi