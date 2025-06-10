#!/usr/bin/env python3
"""
Fix staging database schema issues
"""
import sqlite3
import os

# Get the database path from environment or use default
db_path = os.environ.get('DATABASE_URL', 'sqlite:////app/data/staging_crm.db')
if db_path.startswith('sqlite:///'):
    db_path = db_path.replace('sqlite:///', '')

print(f"Fixing schema in: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='properties'")
    schema = cursor.fetchone()
    if schema:
        print(f"Current properties schema: {schema[0][:100]}...")
    
    # Add missing columns if they don't exist
    fixes = [
        # Fix properties table
        ("ALTER TABLE properties ADD COLUMN street_address TEXT", "properties.street_address"),
        ("UPDATE properties SET street_address = address_line1 WHERE street_address IS NULL", "copy address_line1"),
        
        # Fix transactions table
        ("ALTER TABLE transactions ADD COLUMN earnest_money_amount REAL", "transactions.earnest_money_amount"),
        ("ALTER TABLE transactions ADD COLUMN down_payment_amount REAL", "transactions.down_payment_amount"),
        ("ALTER TABLE transactions ADD COLUMN loan_amount REAL", "transactions.loan_amount"),
        ("ALTER TABLE transactions ADD COLUMN financing_contingency INTEGER DEFAULT 0", "transactions.financing_contingency"),
        ("ALTER TABLE transactions ADD COLUMN inspection_contingency INTEGER DEFAULT 0", "transactions.inspection_contingency"),
        ("ALTER TABLE transactions ADD COLUMN appraisal_contingency INTEGER DEFAULT 0", "transactions.appraisal_contingency"),
        
        # Fix clients table if needed
        ("ALTER TABLE clients ADD COLUMN notes TEXT", "clients.notes"),
        ("ALTER TABLE clients ADD COLUMN status TEXT DEFAULT 'active'", "clients.status"),
        ("ALTER TABLE clients ADD COLUMN lead_source TEXT", "clients.lead_source"),
    ]
    
    for fix_sql, description in fixes:
        try:
            cursor.execute(fix_sql)
            print(f"✓ Applied: {description}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e):
                print(f"  Already exists: {description}")
            else:
                print(f"✗ Failed: {description} - {e}")
    
    conn.commit()
    print("\n✅ Schema fixes applied!")
    
    # Verify
    cursor.execute("PRAGMA table_info(properties)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"\nProperties columns: {', '.join(columns[:10])}...")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")