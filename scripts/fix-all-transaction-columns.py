#!/usr/bin/env python3
"""
Comprehensive fix for ALL transaction table columns based on what the CRM expects
"""

import sqlite3

def get_expected_columns():
    """All columns the CRM code expects in transactions table"""
    return {
        # Core fields (already exist)
        'id': 'INTEGER PRIMARY KEY',
        'client_id': 'INTEGER',
        'property_id': 'INTEGER',
        'transaction_type': 'TEXT',
        'status': 'TEXT',
        'created_at': 'TIMESTAMP',
        
        # Client relationship fields
        'buyer_client_id': 'INTEGER',
        'seller_client_id': 'INTEGER',
        
        # Financial fields
        'purchase_price': 'REAL',
        'earnest_money_amount': 'REAL',
        'down_payment_amount': 'REAL',
        'down_payment_percentage': 'REAL',
        'loan_amount': 'REAL',
        'offer_price': 'REAL',
        'close_of_escrow_date': 'DATE',
        
        # Important dates
        'offer_date': 'DATE',
        'closing_date': 'DATE',
        'contract_date': 'DATE',
        'acceptance_date': 'DATE',
        'possession_date': 'DATE',
        'inspection_deadline': 'DATE',
        'appraisal_deadline': 'DATE',
        'loan_approval_deadline': 'DATE',
        'contingency_removal_date': 'DATE',
        
        # Contingency flags
        'financing_contingency': 'BOOLEAN',
        'inspection_contingency': 'BOOLEAN',
        'appraisal_contingency': 'BOOLEAN',
        'hoa_approval_contingency': 'BOOLEAN',
        'sale_of_buyer_property_contingency': 'BOOLEAN',
        
        # Sale terms
        'as_is_sale': 'BOOLEAN',
        'seller_financing': 'BOOLEAN',
        'home_warranty': 'BOOLEAN',
        'seller_concessions': 'REAL',
        
        # Commission fields
        'buyer_commission': 'REAL',
        'seller_commission': 'REAL',
        'buyer_commission_percentage': 'REAL',
        'seller_commission_percentage': 'REAL',
        'total_commission': 'REAL',
        
        # Property info (denormalized for faster queries)
        'property_street_address': 'TEXT',
        'property_city': 'TEXT',
        'property_state': 'TEXT',
        'property_zip': 'TEXT',
        
        # Names (denormalized)
        'buyer_name': 'TEXT',
        'seller_name': 'TEXT',
        
        # Additional metadata
        'escrow_number': 'TEXT',
        'escrow_company': 'TEXT',
        'title_company': 'TEXT',
        'lender_name': 'TEXT',
        'listing_agent': 'TEXT',
        'selling_agent': 'TEXT',
        'notes': 'TEXT',
        
        # MLS info
        'mls_number': 'TEXT',
        
        # Status tracking
        'last_updated': 'TIMESTAMP',
        'updated_by': 'TEXT'
    }

def fix_all_columns():
    conn = sqlite3.connect('/app/real_estate_crm.db')
    cursor = conn.cursor()
    
    print("🔧 Comprehensive transaction table fix...")
    
    # Get current columns
    cursor.execute("PRAGMA table_info(transactions)")
    existing_columns = {col[1]: col for col in cursor.fetchall()}
    print(f"  Current columns: {len(existing_columns)}")
    
    # Get expected columns
    expected_columns = get_expected_columns()
    print(f"  Expected columns: {len(expected_columns)}")
    
    # Add missing columns
    added = 0
    for col_name, col_type in expected_columns.items():
        if col_name not in existing_columns:
            try:
                # Handle boolean columns as INTEGER
                if col_type == 'BOOLEAN':
                    col_type = 'INTEGER DEFAULT 0'
                    
                cursor.execute(f"ALTER TABLE transactions ADD COLUMN {col_name} {col_type}")
                added += 1
                print(f"  ✅ Added {col_name} ({col_type})")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e):
                    print(f"  ❌ Error adding {col_name}: {e}")
    
    conn.commit()
    
    # Verify final state
    cursor.execute("PRAGMA table_info(transactions)")
    final_columns = [col[1] for col in cursor.fetchall()]
    
    print(f"\n✅ Transaction table fixed!")
    print(f"   Added {added} columns")
    print(f"   Total columns now: {len(final_columns)}")
    
    # Show all columns
    print("\n📋 All transaction columns:")
    for i, col in enumerate(final_columns, 1):
        print(f"   {i:2d}. {col}")
    
    conn.close()

if __name__ == "__main__":
    fix_all_columns()