#!/usr/bin/env python3
"""
Initialize dev database with proper schema and dummy data
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

def init_database():
    """Initialize database with simplified schema that works"""
    
    db_path = '/app/dev_crm.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 Initializing database schema...")
    
    # Drop existing tables if they exist
    cursor.execute("DROP TABLE IF EXISTS transactions")
    cursor.execute("DROP TABLE IF EXISTS properties") 
    cursor.execute("DROP TABLE IF EXISTS clients")
    
    # Create clients table (simplified but functional)
    cursor.execute('''
        CREATE TABLE clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE,
            home_phone TEXT,
            mobile_phone TEXT,
            client_type TEXT DEFAULT 'buyer',
            address TEXT,
            city TEXT,
            state TEXT DEFAULT 'CA',
            zip_code TEXT,
            budget_min REAL,
            budget_max REAL,
            area_preference TEXT,
            bedrooms INTEGER,
            notes TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create properties table
    cursor.execute('''
        CREATE TABLE properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mls_number TEXT UNIQUE,
            property_address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT DEFAULT 'CA',
            zip_code TEXT,
            list_price REAL,
            bedrooms INTEGER,
            bathrooms REAL,
            square_feet INTEGER,
            lot_size REAL,
            year_built INTEGER,
            property_type TEXT,
            status TEXT DEFAULT 'active',
            listing_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            property_id INTEGER,
            transaction_type TEXT,
            offer_price REAL,
            offer_date DATE,
            closing_date DATE,
            escrow_number TEXT,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id),
            FOREIGN KEY (property_id) REFERENCES properties(id)
        )
    ''')
    
    conn.commit()
    print("✅ Schema created successfully")
    
    # Populate with dummy data
    print("📊 Populating with dummy data...")
    
    # Sample data pools
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", "Maria"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    cities = ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "Oakland", "Fresno", "San Jose"]
    
    # Add clients
    clients = []
    for i in range(20):
        client_data = (
            random.choice(first_names),
            random.choice(last_names),
            f"client{i+1}@example.com",
            f"555-{random.randint(1000, 9999)}",
            f"555-{random.randint(1000, 9999)}",
            random.choice(['buyer', 'seller', 'both']),
            f"{random.randint(100, 9999)} Main St",
            random.choice(cities),
            'CA',
            f"{random.randint(90000, 99999)}",
            random.randint(300000, 2000000),
            random.randint(400000, 2500000),
            random.choice(['Downtown', 'Suburbs', 'Waterfront', 'Hills']),
            random.randint(2, 5),
            f"Client interested in {random.choice(['investment', 'primary residence', 'vacation home'])}",
            'active'
        )
        cursor.execute('''
            INSERT INTO clients (first_name, last_name, email, home_phone, mobile_phone,
                               client_type, address, city, state, zip_code,
                               budget_min, budget_max, area_preference, bedrooms, notes, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', client_data)
        clients.append(cursor.lastrowid)
    
    # Add properties
    properties = []
    property_types = ['Single Family', 'Condo', 'Townhouse', 'Multi-Family']
    
    for i in range(30):
        property_data = (
            f"MLS{random.randint(100000, 999999)}",
            f"{random.randint(100, 9999)} {random.choice(['Oak', 'Pine', 'Elm', 'Main', 'First', 'Second'])} St",
            random.choice(cities),
            'CA',
            f"{random.randint(90000, 99999)}",
            random.randint(250000, 3000000),
            random.randint(2, 6),
            random.randint(1, 4) + 0.5,
            random.randint(900, 5000),
            random.randint(2000, 20000) / 1000.0,
            random.randint(1950, 2023),
            random.choice(property_types),
            'active',
            (datetime.now() - timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d')
        )
        cursor.execute('''
            INSERT INTO properties (mls_number, property_address, city, state, zip_code,
                                  list_price, bedrooms, bathrooms, square_feet, lot_size,
                                  year_built, property_type, status, listing_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', property_data)
        properties.append(cursor.lastrowid)
    
    # Add transactions
    for i in range(10):
        transaction_data = (
            random.choice(clients),
            random.choice(properties),
            random.choice(['purchase', 'sale']),
            random.randint(250000, 3000000),
            (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d'),
            f"ESC{random.randint(100000, 999999)}",
            random.choice(['pending', 'in_escrow', 'closed']),
            "Transaction in progress"
        )
        cursor.execute('''
            INSERT INTO transactions (client_id, property_id, transaction_type, offer_price,
                                    offer_date, closing_date, escrow_number, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', transaction_data)
    
    conn.commit()
    
    # Show statistics
    client_count = cursor.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    property_count = cursor.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
    transaction_count = cursor.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    
    print(f"✅ Database populated successfully!")
    print(f"   - Clients: {client_count}")
    print(f"   - Properties: {property_count}")
    print(f"   - Transactions: {transaction_count}")
    
    conn.close()

if __name__ == "__main__":
    init_database()