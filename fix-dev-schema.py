#!/usr/bin/env python3
"""
Fix dev database schema to match what the CRM expects
"""

import sqlite3

def fix_schema():
    conn = sqlite3.connect('/app/dev_crm.db')
    cursor = conn.cursor()
    
    print("🔧 Fixing database schema...")
    
    # Fix properties table - rename property_address to street_address
    cursor.execute("ALTER TABLE properties RENAME COLUMN property_address TO street_address")
    
    # Fix transactions table - add missing columns
    cursor.execute("ALTER TABLE transactions ADD COLUMN purchase_price REAL")
    cursor.execute("ALTER TABLE transactions ADD COLUMN close_of_escrow_date DATE")
    cursor.execute("ALTER TABLE transactions ADD COLUMN property_street_address TEXT")
    cursor.execute("ALTER TABLE transactions ADD COLUMN property_city TEXT")
    cursor.execute("ALTER TABLE transactions ADD COLUMN buyer_name TEXT")
    cursor.execute("ALTER TABLE transactions ADD COLUMN seller_name TEXT")
    
    # Update transaction data
    cursor.execute("""
        UPDATE transactions 
        SET purchase_price = offer_price,
            close_of_escrow_date = closing_date,
            property_street_address = (SELECT street_address FROM properties WHERE properties.id = transactions.property_id),
            property_city = (SELECT city FROM properties WHERE properties.id = transactions.property_id),
            buyer_name = (SELECT first_name || ' ' || last_name FROM clients WHERE clients.id = transactions.client_id),
            seller_name = 'Sample Seller'
    """)
    
    conn.commit()
    print("✅ Schema fixed!")
    
    # Verify fix
    cursor.execute("PRAGMA table_info(properties)")
    print("\nProperties columns:", [col[1] for col in cursor.fetchall()])
    
    cursor.execute("PRAGMA table_info(transactions)")
    print("Transactions columns:", [col[1] for col in cursor.fetchall()])
    
    conn.close()

if __name__ == "__main__":
    fix_schema()