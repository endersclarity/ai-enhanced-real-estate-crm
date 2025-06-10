#!/usr/bin/env python3
"""
Quick database verification script
Checks if real_estate_crm.db exists and has required tables
"""

import sqlite3
import os

def check_database():
    """Check if database exists and has required tables"""
    db_paths = [
        '/home/ender/.claude/projects/offer-creator/core_app/real_estate_crm.db',
        '/home/ender/.claude/projects/offer-creator/real_estate_crm.db',
        '/home/ender/.claude/projects/offer-creator/core_app/database/real_estate_crm.db'
    ]
    
    for db_path in db_paths:
        print(f"\n🔍 Checking: {db_path}")
        
        if os.path.exists(db_path):
            print(f"✅ Database file exists")
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if transactions table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions';")
                transactions_table = cursor.fetchone()
                
                if transactions_table:
                    print("✅ Transactions table exists")
                    
                    # Check table structure
                    cursor.execute("PRAGMA table_info(transactions);")
                    columns = cursor.fetchall()
                    print(f"✅ Transactions table has {len(columns)} columns")
                    
                    # Check if table has data
                    cursor.execute("SELECT COUNT(*) FROM transactions;")
                    count = cursor.fetchone()[0]
                    print(f"📊 Transactions table has {count} records")
                    
                else:
                    print("❌ Transactions table missing")
                
                # List all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"📋 All tables: {[table[0] for table in tables]}")
                
                conn.close()
                return db_path
                
            except Exception as e:
                print(f"❌ Error accessing database: {e}")
        else:
            print(f"❌ Database file does not exist")
    
    return None

if __name__ == "__main__":
    print("🔍 DATABASE VERIFICATION")
    print("=" * 40)
    
    existing_db = check_database()
    
    if existing_db:
        print(f"\n✅ Working database found at: {existing_db}")
    else:
        print(f"\n❌ No working database found. Need to initialize.")
        print("Run: python /home/ender/.claude/projects/offer-creator/core_app/init_database.py")
