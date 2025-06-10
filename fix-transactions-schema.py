#!/usr/bin/env python3
"""
Fix transactions schema to match what the CRM expects
"""

import sqlite3

def fix_transactions():
    conn = sqlite3.connect('/app/real_estate_crm.db')
    cursor = conn.cursor()
    
    print("🔧 Fixing transactions schema...")
    
    try:
        # Check current schema
        cursor.execute("PRAGMA table_info(transactions)")
        columns = {col[1]: col for col in cursor.fetchall()}
        print(f"  Current columns: {list(columns.keys())}")
        
        # The CRM expects buyer_client_id and seller_client_id instead of just client_id
        if 'client_id' in columns and 'buyer_client_id' not in columns:
            print("  - Adding buyer_client_id and seller_client_id columns")
            cursor.execute("ALTER TABLE transactions ADD COLUMN buyer_client_id INTEGER")
            cursor.execute("ALTER TABLE transactions ADD COLUMN seller_client_id INTEGER")
            
            # Copy existing client_id to buyer_client_id (assuming they were buyers)
            cursor.execute("UPDATE transactions SET buyer_client_id = client_id")
            
            print("  - Migrated client_id to buyer_client_id")
        
        # Also add any other missing columns the CRM might expect
        if 'escrow_number' not in columns:
            cursor.execute("ALTER TABLE transactions ADD COLUMN escrow_number TEXT")
            
        if 'notes' not in columns:
            cursor.execute("ALTER TABLE transactions ADD COLUMN notes TEXT")
            
        conn.commit()
        print("✅ Transactions schema fixed!")
        
        # Verify final schema
        cursor.execute("PRAGMA table_info(transactions)")
        print("\nFinal transactions columns:", [col[1] for col in cursor.fetchall()])
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_transactions()