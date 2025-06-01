#!/usr/bin/env python3
import os
import sqlite3
import subprocess
import time

# Kill existing processes
subprocess.run(['pkill', '-f', 'real_estate_crm'], stderr=subprocess.DEVNULL)

# Remove old database
if os.path.exists('real_estate_crm.db'):
    os.remove('real_estate_crm.db')

# Create working database
conn = sqlite3.connect('real_estate_crm.db')
conn.execute('''CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    home_phone TEXT,
    city TEXT,
    client_type TEXT,
    budget_min INTEGER,
    budget_max INTEGER,
    area_preference TEXT,
    bedrooms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')
conn.execute('''CREATE TABLE properties (
    id INTEGER PRIMARY KEY,
    street_address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    price INTEGER,
    bedrooms INTEGER,
    bathrooms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')
conn.execute('''CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    client_id INTEGER,
    property_id INTEGER,
    transaction_type TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

# Add sample data
conn.execute('INSERT INTO clients (first_name, last_name, email, city) VALUES ("John", "Doe", "john@example.com", "Sacramento")')
conn.execute('INSERT INTO properties (street_address, city, state, price) VALUES ("123 Main St", "Sacramento", "CA", 450000)')
conn.execute('INSERT INTO transactions (client_id, property_id, transaction_type) VALUES (1, 1, "purchase")')
conn.commit()
conn.close()

print('✅ Database created with sample data')

# Start Flask
env = os.environ.copy()
env['GEMINI_API_KEY'] = 'AIzaSyCJ8-hQJVLGXDkHy2sjw-O6Dls0FVO0gGU'
subprocess.Popen(['python', 'core_app/real_estate_crm.py'], env=env)

print('🚀 Flask starting...')
time.sleep(3)

# Test connection
try:
    result = subprocess.run(['curl', '-I', 'http://127.0.0.1:5001'], 
                          capture_output=True, text=True, timeout=5)
    if '200 OK' in result.stdout:
        print('✅ Flask confirmed working at http://172.22.206.209:5001')
    else:
        print('⚠️  Flask may have issues, check manually')
except:
    print('⚠️  Could not test connection, check manually')