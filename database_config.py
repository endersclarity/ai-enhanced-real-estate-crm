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

# Global database instance
db = DatabaseConfig()