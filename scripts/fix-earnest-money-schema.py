#!/usr/bin/env python3
"""
Add missing earnest_money_amount column to transactions table
"""

import sqlite3

def fix_schema():
    conn = sqlite3.connect('/app/real_estate_crm.db')
    cursor = conn.cursor()
    
    print("🔧 Adding earnest_money_amount column...")
    
    try:
        # Check current columns
        cursor.execute("PRAGMA table_info(transactions)")
        columns = {col[1]: col for col in cursor.fetchall()}
        
        if 'earnest_money_amount' not in columns:
            cursor.execute("ALTER TABLE transactions ADD COLUMN earnest_money_amount REAL")
            print("✅ Added earnest_money_amount column")
        else:
            print("✅ earnest_money_amount column already exists")
            
        conn.commit()
        
        # Verify
        cursor.execute("PRAGMA table_info(transactions)")
        print("\nCurrent transaction columns:", [col[1] for col in cursor.fetchall()])
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema()