#!/usr/bin/env python3
"""
Database configuration for Real Estate CRM
Supports both SQLite (dev) and Supabase PostgreSQL (production)
"""
import os
import sqlite3
import json
import requests

class DatabaseConfig:
    def __init__(self):
        self.use_supabase = os.environ.get('USE_SUPABASE', 'true').lower() == 'true'
        
        if self.use_supabase:
            # Supabase REST API configuration (more reliable than direct PostgreSQL)
            self.supabase_url = "https://pfcdqrxnjyarhueofrsn.supabase.co"
            self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBmY2Rxcnhuanlhcmh1ZW9mcnNuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg4MTUyMzEsImV4cCI6MjA2NDM5MTIzMX0.04ZvxzZn43utA1SNnqTvhjquhI801gNDcH-rJTMbIzA"
            self.headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
        else:
            # SQLite configuration (local development)
            self.sqlite_path = 'real_estate_crm.db'
    
    def get_all_clients(self):
        """Get all clients from the database"""
        if self.use_supabase:
            # Use Supabase REST API
            response = requests.get(
                f"{self.supabase_url}/rest/v1/clients?select=*&order=last_name.asc,first_name.asc",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Supabase error: {response.status_code} - {response.text}")
                return []
        else:
            # SQLite fallback
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, client_type, first_name, last_name, email, home_phone, 
                       city, created_at
                FROM clients 
                ORDER BY last_name, first_name
            ''')
            clients = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return clients
    
    def get_connection(self):
        """Get database connection based on configuration"""
        if not self.use_supabase:
            return sqlite3.connect(self.sqlite_path)
        return None  # Supabase uses REST API, no direct connection
    
    def execute_query(self, query, params=None, fetch_all=False, fetch_one=False):
        """Execute a database query with automatic connection handling"""
        if self.use_supabase:
            # For now, use REST API for simple queries
            if "COUNT(*)" in query and "clients" in query:
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/clients?select=count",
                    headers=self.headers
                )
                if response.status_code == 200:
                    data = response.json()
                    return [len(data)] if fetch_one else [[len(data)]]
            return [] if fetch_all else None
        else:
            # SQLite fallback
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row  # This makes rows behave like dictionaries
            try:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                
                if fetch_all:
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]  # Convert to dictionaries
                elif fetch_one:
                    row = cursor.fetchone()
                    return dict(row) if row else None  # Convert to dictionary
                else:
                    conn.commit()
                    return cursor.rowcount
            finally:
                conn.close()
    
    def init_database_schema(self):
        """Initialize database schema if using SQLite"""
        if not self.use_supabase:
            conn = sqlite3.connect(self.sqlite_path)
            try:
                cursor = conn.cursor()
                
                # Create clients table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS clients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_type TEXT NOT NULL,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        email TEXT UNIQUE,
                        home_phone TEXT,
                        city TEXT,
                        status TEXT DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create properties table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS properties (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        property_address TEXT NOT NULL,
                        city TEXT,
                        state TEXT DEFAULT 'CA',
                        zip_code TEXT,
                        listing_price DECIMAL(12,2),
                        property_type TEXT DEFAULT 'Single Family Home',
                        bedrooms INTEGER,
                        bathrooms DECIMAL(3,1),
                        square_feet INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create transactions table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_id INTEGER,
                        property_id INTEGER,
                        transaction_type TEXT,
                        purchase_price DECIMAL(12,2),
                        offer_date DATE,
                        closing_date DATE,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (client_id) REFERENCES clients (id),
                        FOREIGN KEY (property_id) REFERENCES properties (id)
                    )
                ''')
                
                # Add sample data if tables are empty
                cursor.execute('SELECT COUNT(*) FROM clients')
                if cursor.fetchone()[0] == 0:
                    # Add sample clients
                    sample_clients = [
                        ('buyer', 'John', 'Smith', 'john.smith@email.com', '916-555-0101', 'Sacramento'),
                        ('seller', 'Mary', 'Johnson', 'mary.johnson@email.com', '916-555-0102', 'Sacramento'),
                        ('buyer', 'Robert', 'Williams', 'robert.williams@email.com', '916-555-0103', 'Roseville'),
                        ('seller', 'Jennifer', 'Brown', 'jennifer.brown@email.com', '916-555-0104', 'Folsom'),
                    ]
                    cursor.executemany(
                        'INSERT INTO clients (client_type, first_name, last_name, email, home_phone, city) VALUES (?, ?, ?, ?, ?, ?)',
                        sample_clients
                    )
                
                cursor.execute('SELECT COUNT(*) FROM properties')
                if cursor.fetchone()[0] == 0:
                    # Add sample properties
                    sample_properties = [
                        ('123 Main St', 'Sacramento', 'CA', '95814', 450000.00, 'Single Family Home', 3, 2.0, 1200),
                        ('456 Oak Ave', 'Sacramento', 'CA', '95825', 520000.00, 'Single Family Home', 4, 2.5, 1450),
                        ('789 Pine St', 'Roseville', 'CA', '95661', 380000.00, 'Townhouse', 2, 2.0, 1100),
                        ('321 Elm Dr', 'Folsom', 'CA', '95630', 675000.00, 'Single Family Home', 4, 3.0, 2100),
                    ]
                    cursor.executemany(
                        'INSERT INTO properties (property_address, city, state, zip_code, listing_price, property_type, bedrooms, bathrooms, square_feet) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        sample_properties
                    )
                
                cursor.execute('SELECT COUNT(*) FROM transactions')
                if cursor.fetchone()[0] == 0:
                    # Add sample transactions with proper relationships
                    sample_transactions = [
                        (1, 1, 'purchase', 450000.00, '2025-06-01', '2025-07-15', 'active'),
                        (3, 2, 'purchase', 520000.00, '2025-06-05', '2025-07-20', 'under_contract'),
                        (1, 3, 'purchase', 380000.00, '2025-05-28', '2025-06-28', 'closed'),
                        (3, 4, 'purchase', 675000.00, '2025-06-08', '2025-08-01', 'pending'),
                    ]
                    cursor.executemany(
                        'INSERT INTO transactions (client_id, property_id, transaction_type, purchase_price, offer_date, closing_date, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        sample_transactions
                    )
                
                conn.commit()
                print("✅ SQLite database schema initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing database schema: {e}")
            finally:
                conn.close()
        else:
            print("✅ Using Supabase - schema managed remotely")

    def get_clients_summary(self):
        """Get client statistics for dashboard"""
        if self.use_supabase:
            try:
                # Get all clients from Supabase
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/clients",
                    headers=self.headers
                )
                if response.status_code == 200:
                    clients = response.json()
                    total_clients = len(clients)
                    buyers = len([c for c in clients if c.get('client_type') == 'buyer'])
                    sellers = len([c for c in clients if c.get('client_type') == 'seller'])
                    active_clients = len([c for c in clients if c.get('status') == 'active'])
                    
                    return {
                        'total_clients': total_clients,
                        'buyers': buyers,
                        'sellers': sellers,
                        'active_clients': active_clients
                    }
            except Exception as e:
                print(f"Error fetching clients from Supabase: {e}")
                return {'total_clients': 0, 'buyers': 0, 'sellers': 0, 'active_clients': 0}
        else:
            # SQLite fallback
            query = """
                SELECT 
                    COUNT(*) as total_clients,
                    COUNT(CASE WHEN client_type = 'buyer' THEN 1 END) as buyers,
                    COUNT(CASE WHEN client_type = 'seller' THEN 1 END) as sellers,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_clients
                FROM clients
            """
            result = self.execute_query(query, fetch_one=True)
            if result:
                return {
                    'total_clients': result[0] or 0,
                    'buyers': result[1] or 0,
                    'sellers': result[2] or 0,
                    'active_clients': result[3] or 0
                }
        
        return {'total_clients': 0, 'buyers': 0, 'sellers': 0, 'active_clients': 0}

# Global database instance
db = DatabaseConfig()