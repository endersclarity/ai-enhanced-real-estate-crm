#!/bin/bash
# Simple database check

echo "🔍 CHECKING DATABASE IN CONTAINER"
echo "================================="

# Run database check directly
docker-compose -f docker-compose.dev.yml exec app bash -c "
ls -la *.db 2>/dev/null || echo 'No .db files in app root'
ls -la database/*.db 2>/dev/null || echo 'No .db files in database/'
python -c \"
import sqlite3
import os
print('Current dir:', os.getcwd())
if os.path.exists('real_estate_crm.db'):
    print('✅ real_estate_crm.db exists')
    conn = sqlite3.connect('real_estate_crm.db')
    cursor = conn.cursor()
    cursor.execute(\\\"SELECT name FROM sqlite_master WHERE type='table';\\\")
    tables = [t[0] for t in cursor.fetchall()]
    print('Tables:', tables)
    print('Transactions table exists:', 'transactions' in tables)
    conn.close()
else:
    print('❌ real_estate_crm.db does not exist')
\"
"