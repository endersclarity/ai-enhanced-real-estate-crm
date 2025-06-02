#!/usr/bin/env python3
"""
Database configuration for Real Estate CRM
Supports both SQLite (dev) and Supabase PostgreSQL (production)
"""
import os
import sqlite3
import json
import requests
from datetime import datetime

class DatabaseConfig:
    def __init__(self):
        self.use_supabase = os.environ.get('USE_SUPABASE', 'true').lower() == 'true'
        
        if self.use_supabase:
            # Load from supabase_config.env if available
            self._load_supabase_config()
            self.headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
        else:
            # SQLite configuration (local development)
            self.sqlite_path = 'real_estate_crm.db'
    
    def _load_supabase_config(self):
        """Load Supabase configuration from environment or config file"""
        # Try environment variables first
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        # If not found, try loading from supabase_config.env
        if not self.supabase_url or not self.supabase_key:
            config_file = 'supabase_config.env'
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    for line in f:
                        if line.startswith('SUPABASE_URL='):
                            self.supabase_url = line.split('=', 1)[1].strip()
                        elif line.startswith('SUPABASE_ANON_KEY='):
                            self.supabase_key = line.split('=', 1)[1].strip()
        
        # Fallback to hardcoded values
        if not self.supabase_url:
            self.supabase_url = "https://pfcdqrxnjyarhueofrsn.supabase.co"
        if not self.supabase_key:
            self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBmY2Rxcnhuanlhcmh1ZW9mcnNuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg4MTUyMzEsImV4cCI6MjA2NDM5MTIzMX0.04ZvxzZn43utA1SNnqTvhjquhI801gNDcH-rJTMbIzA"
    
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
            try:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                
                if fetch_all:
                    return cursor.fetchall()
                elif fetch_one:
                    return cursor.fetchone()
                else:
                    conn.commit()
                    return cursor.rowcount
            finally:
                conn.close()
    
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
    
    def init_database_schema(self):
        """Initialize database schema (Supabase schema already exists)"""
        if self.use_supabase:
            print("✅ Using existing Supabase PostgreSQL schema (177 fields)")
            # Verify connection
            try:
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/clients?select=count",
                    headers=self.headers
                )
                if response.status_code == 200:
                    print("✅ Supabase connection verified")
                    return True
                else:
                    print(f"❌ Supabase connection failed: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ Supabase connection error: {e}")
                return False
        else:
            # Create SQLite schema
            return self._init_sqlite_schema()
    
    def _init_sqlite_schema(self):
        """Initialize SQLite schema for local development"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            
            # Create basic tables
            conn.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    email VARCHAR(255),
                    client_type VARCHAR(50) DEFAULT 'buyer',
                    status VARCHAR(50) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS properties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    street_address VARCHAR(255),
                    city VARCHAR(100),
                    state VARCHAR(50),
                    zip_code VARCHAR(20),
                    listed_price DECIMAL(15,2),
                    status VARCHAR(50) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    property_id INTEGER,
                    purchase_price DECIMAL(15,2),
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert sample data if empty
            if conn.execute('SELECT COUNT(*) FROM clients').fetchone()[0] == 0:
                conn.execute('''
                    INSERT INTO clients (first_name, last_name, email, client_type)
                    VALUES ('John', 'Smith', 'john.smith@email.com', 'buyer')
                ''')
            
            conn.commit()
            conn.close()
            print("✅ SQLite database schema initialized")
            return True
            
        except Exception as e:
            print(f"❌ SQLite schema initialization error: {e}")
            return False
    
    def create_client(self, data):
        """Create a new client record"""
        if self.use_supabase:
            try:
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/clients",
                    headers=self.headers,
                    json=data
                )
                return response.status_code == 201
            except Exception as e:
                print(f"Error creating client in Supabase: {e}")
                return False
        else:
            # SQLite fallback
            try:
                conn = sqlite3.connect(self.sqlite_path)
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?' for _ in data])
                query = f"INSERT INTO clients ({columns}) VALUES ({placeholders})"
                conn.execute(query, list(data.values()))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Error creating client in SQLite: {e}")
                return False
    
    def create_property(self, data):
        """Create a new property record"""
        if self.use_supabase:
            try:
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/properties",
                    headers=self.headers,
                    json=data
                )
                return response.status_code == 201
            except Exception as e:
                print(f"Error creating property in Supabase: {e}")
                return False
        else:
            # SQLite fallback
            try:
                conn = sqlite3.connect(self.sqlite_path)
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?' for _ in data])
                query = f"INSERT INTO properties ({columns}) VALUES ({placeholders})"
                conn.execute(query, list(data.values()))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Error creating property in SQLite: {e}")
                return False
    
    def get_all_clients(self):
        """Get all client records"""
        if self.use_supabase:
            try:
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/clients",
                    headers=self.headers
                )
                if response.status_code == 200:
                    return response.json()
                return []
            except Exception as e:
                print(f"Error fetching clients from Supabase: {e}")
                return []
        else:
            # SQLite fallback
            try:
                conn = sqlite3.connect(self.sqlite_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM clients")
                rows = cursor.fetchall()
                conn.close()
                return [dict(row) for row in rows]
            except Exception as e:
                print(f"Error fetching clients from SQLite: {e}")
                return []
    
    def get_all_properties(self):
        """Get all property records"""
        if self.use_supabase:
            try:
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/properties",
                    headers=self.headers
                )
                if response.status_code == 200:
                    return response.json()
                return []
            except Exception as e:
                print(f"Error fetching properties from Supabase: {e}")
                return []
        else:
            # SQLite fallback
            try:
                conn = sqlite3.connect(self.sqlite_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM properties")
                rows = cursor.fetchall()
                conn.close()
                return [dict(row) for row in rows]
            except Exception as e:
                print(f"Error fetching properties from SQLite: {e}")
                return []

# Global database instance
db = DatabaseConfig()