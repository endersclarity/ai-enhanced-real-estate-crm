#!/usr/bin/env python3
"""
Add the remaining missing columns
"""

import sqlite3

def fix_remaining_columns():
    conn = sqlite3.connect('/app/real_estate_crm.db')
    cursor = conn.cursor()
    
    print("🔧 Adding remaining missing columns...")
    
    # Get current columns
    cursor.execute("PRAGMA table_info(transactions)")
    existing_columns = {col[1]: col for col in cursor.fetchall()}
    
    # Missing columns from the INSERT statement
    missing_columns = {
        'loan_term_years': 'INTEGER',
        'interest_rate': 'REAL',
        'title_contingency': 'INTEGER DEFAULT 0',
        'sale_of_property_contingency': 'INTEGER DEFAULT 0',
        'homeowners_insurance_contingency': 'INTEGER DEFAULT 0'
    }
    
    added = 0
    for col_name, col_type in missing_columns.items():
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE transactions ADD COLUMN {col_name} {col_type}")
                added += 1
                print(f"  ✅ Added {col_name} ({col_type})")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e):
                    print(f"  ❌ Error adding {col_name}: {e}")
    
    conn.commit()
    
    print(f"\n✅ Added {added} more columns")
    
    # Final verification
    cursor.execute("PRAGMA table_info(transactions)")
    final_count = len(cursor.fetchall())
    print(f"   Total columns now: {final_count}")
    
    conn.close()

if __name__ == "__main__":
    fix_remaining_columns()