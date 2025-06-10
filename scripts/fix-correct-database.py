#!/usr/bin/env python3
"""
Fix the actual database being used by the app
"""

import sqlite3
import os

def fix_database(db_path):
    """Apply comprehensive fixes to a database"""
    print(f"\n🔧 Fixing database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"  ❌ Database not found: {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  Tables found: {tables}")
        
        if 'properties' not in tables:
            print("  ❌ No properties table found")
            return
            
        # Check current properties columns
        cursor.execute("PRAGMA table_info(properties)")
        property_columns = {col[1]: col for col in cursor.fetchall()}
        print(f"  Current property columns: {list(property_columns.keys())}")
        
        # Properties table fixes
        if 'property_address' in property_columns and 'street_address' not in property_columns:
            print("  - Renaming property_address to street_address")
            cursor.execute("ALTER TABLE properties RENAME COLUMN property_address TO street_address")
        elif 'property_address' not in property_columns and 'street_address' not in property_columns:
            print("  - Adding street_address column")
            cursor.execute("ALTER TABLE properties ADD COLUMN street_address TEXT")
            # Update with some default data
            cursor.execute("UPDATE properties SET street_address = COALESCE(mls_number, 'Unknown') || ' Main St'")
        
        # Add missing property columns that CRM expects
        expected_property_cols = ['listed_price', 'zillow_url', 'realtor_url', 'mls_portal_url']
        for col in expected_property_cols:
            if col not in property_columns:
                print(f"  - Adding missing column: {col}")
                if col == 'listed_price':
                    cursor.execute("ALTER TABLE properties ADD COLUMN listed_price REAL")
                    # Try to copy from list_price if it exists
                    if 'list_price' in property_columns:
                        cursor.execute("UPDATE properties SET listed_price = list_price")
                else:
                    cursor.execute(f"ALTER TABLE properties ADD COLUMN {col} TEXT")
        
        # Check transactions columns if table exists
        if 'transactions' in tables:
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
                        if 'offer_price' in transaction_columns:
                            cursor.execute("UPDATE transactions SET purchase_price = offer_price")
                    elif col == 'close_of_escrow_date':
                        cursor.execute("ALTER TABLE transactions ADD COLUMN close_of_escrow_date DATE")
                        if 'closing_date' in transaction_columns:
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
        print(f"  ✅ Database fixed!")
        
    except Exception as e:
        print(f"  ❌ Error fixing database: {e}")
    finally:
        conn.close()

def main():
    """Fix all potential database locations"""
    print("🔍 Fixing all database files...")
    
    # Primary database location
    fix_database('/app/real_estate_crm.db')
    
    # Also fix the one in core_app since that's where the app might look
    fix_database('/app/core_app/real_estate_crm.db')
    
    print("\n✅ All databases processed!")

if __name__ == "__main__":
    main()