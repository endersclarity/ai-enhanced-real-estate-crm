#!/usr/bin/env python3
"""
Final database fix - handle views and constraints properly
"""

import sqlite3

def fix_database():
    conn = sqlite3.connect('/app/real_estate_crm.db')
    cursor = conn.cursor()
    
    print("🔧 Final database fix...")
    
    try:
        # First, drop any views that might reference the old column names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        views = [row[0] for row in cursor.fetchall()]
        for view in views:
            print(f"  - Dropping view: {view}")
            cursor.execute(f"DROP VIEW IF EXISTS {view}")
        
        # Now we can safely rename the column
        cursor.execute("PRAGMA table_info(properties)")
        columns = {col[1]: col for col in cursor.fetchall()}
        
        if 'property_address' in columns and 'street_address' not in columns:
            print("  - Creating new properties table with correct schema")
            # SQLite doesn't support column rename on older versions, so recreate table
            cursor.execute("""
                CREATE TABLE properties_new (
                    id INTEGER PRIMARY KEY,
                    street_address TEXT,
                    city TEXT,
                    state TEXT,
                    zip_code TEXT,
                    listing_price REAL,
                    listed_price REAL,
                    property_type TEXT,
                    bedrooms INTEGER,
                    bathrooms REAL,
                    square_feet INTEGER,
                    created_at TIMESTAMP,
                    mls_number TEXT,
                    zillow_url TEXT,
                    realtor_url TEXT,
                    mls_portal_url TEXT
                )
            """)
            
            # Copy data
            cursor.execute("""
                INSERT INTO properties_new 
                (id, street_address, city, state, zip_code, listing_price, listed_price,
                 property_type, bedrooms, bathrooms, square_feet, created_at)
                SELECT id, property_address, city, state, zip_code, listing_price, listing_price,
                       property_type, bedrooms, bathrooms, square_feet, created_at
                FROM properties
            """)
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE properties")
            cursor.execute("ALTER TABLE properties_new RENAME TO properties")
            print("  ✅ Properties table recreated with correct schema")
        
        # Fix transactions table
        cursor.execute("PRAGMA table_info(transactions)")
        trans_columns = {col[1]: col for col in cursor.fetchall()}
        
        expected_cols = {
            'purchase_price': 'REAL',
            'close_of_escrow_date': 'DATE',
            'property_street_address': 'TEXT',
            'property_city': 'TEXT', 
            'buyer_name': 'TEXT',
            'seller_name': 'TEXT'
        }
        
        for col, col_type in expected_cols.items():
            if col not in trans_columns:
                print(f"  - Adding {col} to transactions")
                cursor.execute(f"ALTER TABLE transactions ADD COLUMN {col} {col_type}")
        
        # Update transaction data
        if 'offer_price' in trans_columns:
            cursor.execute("UPDATE transactions SET purchase_price = offer_price WHERE purchase_price IS NULL")
        if 'closing_date' in trans_columns:
            cursor.execute("UPDATE transactions SET close_of_escrow_date = closing_date WHERE close_of_escrow_date IS NULL")
        
        # Update property references
        cursor.execute("""
            UPDATE transactions 
            SET property_street_address = (
                SELECT street_address FROM properties 
                WHERE properties.id = transactions.property_id
            )
            WHERE property_street_address IS NULL
        """)
        
        cursor.execute("""
            UPDATE transactions 
            SET property_city = (
                SELECT city FROM properties 
                WHERE properties.id = transactions.property_id  
            )
            WHERE property_city IS NULL
        """)
        
        # Set default values
        cursor.execute("UPDATE transactions SET buyer_name = 'Unknown Buyer' WHERE buyer_name IS NULL")
        cursor.execute("UPDATE transactions SET seller_name = 'Unknown Seller' WHERE seller_name IS NULL")
        
        conn.commit()
        print("✅ Database fixed successfully!")
        
        # Verify
        cursor.execute("PRAGMA table_info(properties)")
        print("\nFinal properties columns:", [col[1] for col in cursor.fetchall()])
        
        cursor.execute("PRAGMA table_info(transactions)")
        print("Final transactions columns:", [col[1] for col in cursor.fetchall()])
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database()