#!/bin/bash
# Initialize database in container

echo "🔧 INITIALIZING DATABASE IN CONTAINER"
echo "====================================="

# Initialize the database
docker-compose -f docker-compose.dev.yml exec app bash -c "
cd core_app
python init_database.py
echo 'Database initialization complete'
"

echo ""
echo "🔍 VERIFYING DATABASE AFTER INIT"
echo "================================"

# Verify the database was created
docker-compose -f docker-compose.dev.yml exec app bash -c "
python -c \"
import sqlite3
import os

if os.path.exists('real_estate_crm.db'):
    print('✅ Database exists in app root')
    conn = sqlite3.connect('real_estate_crm.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\\\"table\\\";')
    tables = [t[0] for t in cursor.fetchall()]
    print('📋 Tables found:', tables)
    
    if 'transactions' in tables:
        print('✅ Transactions table exists')
        cursor.execute('PRAGMA table_info(transactions);')
        columns = cursor.fetchall()
        print(f'📊 Transactions table has {len(columns)} columns')
    else:
        print('❌ Transactions table missing')
    
    conn.close()
else:
    print('❌ Database still does not exist')
\"
"