#!/usr/bin/env python3
import sqlite3
from datetime import datetime

# Create a fresh database with proper permissions
conn = sqlite3.connect('test_crm.db')
cursor = conn.cursor()

# Create transaction table
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_name TEXT,
    seller_name TEXT,
    property_address TEXT,
    purchase_price REAL,
    closing_date TEXT,
    created_date TEXT
)
''')

# Insert test transaction
cursor.execute('''
INSERT INTO transactions (buyer_name, seller_name, property_address, purchase_price, closing_date, created_date)
VALUES (?, ?, ?, ?, ?, ?)
''', (
    'John Michael Smith',
    'Sarah Jane Wilson', 
    '123 Main Street, Sacramento, CA 95814',
    450000.00,
    '2025-08-15',
    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
))

# Insert a second test transaction
cursor.execute('''
INSERT INTO transactions (buyer_name, seller_name, property_address, purchase_price, closing_date, created_date)
VALUES (?, ?, ?, ?, ?, ?)
''', (
    'Michael Rodriguez',
    'Jennifer Davis',
    '456 Oak Avenue, Sacramento, CA 95816', 
    750000.00,
    '2025-09-30',
    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
))

conn.commit()

# Verify the data
cursor.execute('SELECT * FROM transactions')
transactions = cursor.fetchall()

print('🎯 TRANSACTION RECORDS CREATED!')
print('=' * 40)
for i, transaction in enumerate(transactions, 1):
    print(f'Transaction #{i}:')
    print(f'  ID: {transaction[0]}')
    print(f'  Buyer: {transaction[1]}')
    print(f'  Seller: {transaction[2]}')
    print(f'  Property: {transaction[3]}')
    print(f'  Price: ')
    print(f'  Closing: {transaction[5]}')
    print()

print(f'✅ Database created: test_crm.db')
print(f'✅ {len(transactions)} transaction records available for form generator testing')

conn.close()
