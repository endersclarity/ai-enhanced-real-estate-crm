#!/usr/bin/env python3
"""
Comprehensive schema fix to ensure database matches what CRM expects
"""

import sqlite3

def fix_schema():
    conn = sqlite3.connect('/app/dev_crm.db')
    cursor = conn.cursor()
    
    print("🔧 Comprehensive database schema fix...")
    
    # Check current properties columns
    cursor.execute("PRAGMA table_info(properties)")
    property_columns = {col[1]: col for col in cursor.fetchall()}
    
    # Properties table fixes
    if 'property_address' in property_columns and 'street_address' not in property_columns:
        print("  - Renaming property_address to street_address")
        cursor.execute("ALTER TABLE properties RENAME COLUMN property_address TO street_address")
    elif 'property_address' not in property_columns and 'street_address' not in property_columns:
        print("  - Adding street_address column")
        cursor.execute("ALTER TABLE properties ADD COLUMN street_address TEXT")
        cursor.execute("UPDATE properties SET street_address = mls_number || ' Main St'")
    
    # Add missing property columns that CRM expects
    expected_property_cols = ['listed_price', 'zillow_url', 'realtor_url', 'mls_portal_url']
    for col in expected_property_cols:
        if col not in property_columns:
            print(f"  - Adding missing column: {col}")
            if col == 'listed_price':
                cursor.execute("ALTER TABLE properties ADD COLUMN listed_price REAL")
                cursor.execute("UPDATE properties SET listed_price = list_price")
            else:
                cursor.execute(f"ALTER TABLE properties ADD COLUMN {col} TEXT")
    
    # Check transactions columns
    cursor.execute("PRAGMA table_info(transactions)")
    transaction_columns = {col[1]: col for col in cursor.fetchall()}
    
    # Transactions table fixes
    expected_trans_cols = ['purchase_price', 'close_of_escrow_date', 'property_street_address', 
                          'property_city', 'buyer_name', 'seller_name']
    
    for col in expected_trans_cols:
        if col not in transaction_columns:
            print(f"  - Adding missing transaction column: {col}")
            if col == 'purchase_price':
                cursor.execute("ALTER TABLE transactions ADD COLUMN purchase_price REAL")
                cursor.execute("UPDATE transactions SET purchase_price = offer_price")
            elif col == 'close_of_escrow_date':
                cursor.execute("ALTER TABLE transactions ADD COLUMN close_of_escrow_date DATE")
                cursor.execute("UPDATE transactions SET close_of_escrow_date = closing_date")
            elif col == 'property_street_address':
                cursor.execute("ALTER TABLE transactions ADD COLUMN property_street_address TEXT")
                cursor.execute("""
                    UPDATE transactions 
                    SET property_street_address = (
                        SELECT street_address FROM properties 
                        WHERE properties.id = transactions.property_id
                    )
                """)
            elif col == 'property_city':
                cursor.execute("ALTER TABLE transactions ADD COLUMN property_city TEXT")
                cursor.execute("""
                    UPDATE transactions 
                    SET property_city = (
                        SELECT city FROM properties 
                        WHERE properties.id = transactions.property_id
                    )
                """)
            elif col == 'buyer_name':
                cursor.execute("ALTER TABLE transactions ADD COLUMN buyer_name TEXT")
                cursor.execute("""
                    UPDATE transactions 
                    SET buyer_name = (
                        SELECT first_name || ' ' || last_name FROM clients 
                        WHERE clients.id = transactions.client_id
                    )
                """)
            elif col == 'seller_name':
                cursor.execute("ALTER TABLE transactions ADD COLUMN seller_name TEXT")
                cursor.execute("UPDATE transactions SET seller_name = 'Sample Seller'")
    
    conn.commit()
    print("✅ Schema comprehensively fixed!")
    
    # Verify final state
    cursor.execute("PRAGMA table_info(properties)")
    print("\nFinal properties columns:", [col[1] for col in cursor.fetchall()])
    
    cursor.execute("PRAGMA table_info(transactions)")
    print("Final transactions columns:", [col[1] for col in cursor.fetchall()])
    
    conn.close()

if __name__ == "__main__":
    fix_schema()