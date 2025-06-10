#!/bin/bash
# Database verification script for Docker container

echo "🔍 VERIFYING DATABASE INSIDE CONTAINER"
echo "======================================"

# Check database inside the running container
docker-compose -f docker-compose.dev.yml exec app python -c "
import sqlite3
import os

print('📁 Current working directory:', os.getcwd())
print('📁 Directory contents:')
for item in os.listdir('.'):
    print(f'  {item}')

# Check for database files
db_files = []
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.db'):
            db_files.append(os.path.join(root, file))

print(f'\\n💾 Found database files: {db_files}')

# Test the specific database the app is trying to use
app_db_path = 'real_estate_crm.db'
print(f'\\n🎯 Testing app database: {app_db_path}')

if os.path.exists(app_db_path):
    print('✅ Database file exists')
    try:
        conn = sqlite3.connect(app_db_path)
        cursor = conn.cursor()
        
        # Check for transactions table
        cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='transactions';\")
        result = cursor.fetchone()
        
        if result:
            print('✅ Transactions table exists')
        else:
            print('❌ Transactions table missing')
            
        # List all tables
        cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table';\")
        tables = cursor.fetchall()
        print(f'📋 All tables: {[t[0] for t in tables]}')
        
        conn.close()
    except Exception as e:
        print(f'❌ Database error: {e}')
else:
    print('❌ Database file does not exist')
"
