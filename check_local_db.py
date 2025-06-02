#!/usr/bin/env python3
"""
Check Local SQLite Database Content
Real Estate CRM - Data Migration Analysis
"""

import sqlite3
import os

def check_database(db_path):
    """Check what data is in the local SQLite database"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    print(f"🔍 Checking database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("📋 No tables found in database")
            return
        
        print(f"📋 Found {len(tables)} tables:")
        
        for table in tables:
            table_name = table[0]
            print(f"\n🗂️  Table: {table_name}")
            
            # Count rows
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   📊 Rows: {count}")
            
            if count > 0:
                # Show first few rows
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                
                # Get column names
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                
                print(f"   🏷️  Columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
                
                if rows:
                    print("   📝 Sample data:")
                    for i, row in enumerate(rows):
                        # Show first few columns only
                        sample = str(row[:3]) + "..." if len(row) > 3 else str(row)
                        print(f"      Row {i+1}: {sample}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {str(e)}")

if __name__ == "__main__":
    print("🏠 Real Estate CRM - Local Database Analysis\n")
    
    # Check both database files
    databases = ["real_estate_crm.db", "real_estate.db"]
    
    for db in databases:
        if os.path.exists(db):
            check_database(db)
            print("\n" + "="*50 + "\n")
        else:
            print(f"⚠️  Database not found: {db}\n")