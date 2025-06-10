#!/usr/bin/env python3
"""
Standardize database schema across all environments
This migration ensures column names match what the code expects
"""

import sqlite3
import sys
import os

def migrate_database(db_path):
    """Apply schema standardization to a database"""
    print(f"\n📁 Migrating: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"  ❌ Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get current schema info
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"  📊 Found tables: {', '.join(tables)}")
    
    migrations_applied = []
    
    # 1. Standardize properties table
    cursor.execute("PRAGMA table_info(properties)")
    columns = {col[1]: col for col in cursor.fetchall()}
    
    if 'address' in columns and 'street_address' not in columns:
        print("  🔧 Renaming address → street_address")
        cursor.execute("ALTER TABLE properties ADD COLUMN street_address TEXT")
        cursor.execute("UPDATE properties SET street_address = address")
        migrations_applied.append("properties.street_address")
    elif 'street_address' not in columns and 'address_line1' in columns:
        print("  🔧 Creating street_address from address_line1")
        cursor.execute("ALTER TABLE properties ADD COLUMN street_address TEXT")
        cursor.execute("UPDATE properties SET street_address = address_line1")
        migrations_applied.append("properties.street_address")
    
    # 2. Add all transaction columns that might be missing
    transaction_columns = {
        'earnest_money_amount': 'REAL',
        'down_payment_amount': 'REAL',
        'loan_amount': 'REAL',
        'financing_contingency': 'INTEGER DEFAULT 0',
        'inspection_contingency': 'INTEGER DEFAULT 0',
        'appraisal_contingency': 'INTEGER DEFAULT 0',
        'title_contingency': 'INTEGER DEFAULT 0',
        'sale_of_property_contingency': 'INTEGER DEFAULT 0',
        'homeowners_insurance_contingency': 'INTEGER DEFAULT 0',
        'hoa_approval_contingency': 'INTEGER DEFAULT 0',
        'closing_cost_paid_by': 'TEXT',
        'personal_property_included': 'TEXT',
        'additional_terms': 'TEXT',
        'contingency_removal_date': 'TEXT',
        'offer_expiration_date': 'TEXT',
        'possession_date': 'TEXT',
        'home_warranty': 'INTEGER DEFAULT 0',
        'home_warranty_provider': 'TEXT',
        'title_company': 'TEXT',
        'escrow_company': 'TEXT',
        'attorney_name': 'TEXT',
        'broker_name': 'TEXT',
        'agent_name': 'TEXT',
        'agent_license': 'TEXT',
        'broker_license': 'TEXT',
        'commission_percentage': 'REAL',
        'listing_agent_name': 'TEXT',
        'listing_agent_license': 'TEXT',
        'listing_broker_name': 'TEXT',
        'listing_broker_license': 'TEXT',
        'mls_number': 'TEXT',
        'legal_description': 'TEXT',
        'assessor_parcel_number': 'TEXT',
        'property_tax_amount': 'REAL',
        'hoa_fee': 'REAL',
        'other_fees': 'TEXT',
        'rent_back_requested': 'INTEGER DEFAULT 0',
        'rent_back_daily_rate': 'REAL',
        'seller_concessions_amount': 'REAL',
        'repair_request_amount': 'REAL',
        'as_is_sale': 'INTEGER DEFAULT 0',
        'seller_financing': 'INTEGER DEFAULT 0',
        'assumable_loan': 'INTEGER DEFAULT 0',
        'occupancy_status': 'TEXT'
    }
    
    cursor.execute("PRAGMA table_info(transactions)")
    existing_cols = {col[1] for col in cursor.fetchall()}
    
    for col_name, col_type in transaction_columns.items():
        if col_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE transactions ADD COLUMN {col_name} {col_type}")
                migrations_applied.append(f"transactions.{col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e):
                    print(f"  ⚠️  Failed to add {col_name}: {e}")
    
    # 3. Ensure clients table has all needed columns
    client_columns = {
        'notes': 'TEXT',
        'status': 'TEXT DEFAULT "active"',
        'lead_source': 'TEXT',
        'budget_min': 'REAL',
        'budget_max': 'REAL',
        'area_preference': 'TEXT'
    }
    
    cursor.execute("PRAGMA table_info(clients)")
    existing_client_cols = {col[1] for col in cursor.fetchall()}
    
    for col_name, col_type in client_columns.items():
        if col_name not in existing_client_cols:
            try:
                cursor.execute(f"ALTER TABLE clients ADD COLUMN {col_name} {col_type}")
                migrations_applied.append(f"clients.{col_name}")
            except sqlite3.OperationalError:
                pass
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"  ✅ Applied {len(migrations_applied)} migrations")
    if migrations_applied:
        print(f"     {', '.join(migrations_applied[:5])}{'...' if len(migrations_applied) > 5 else ''}")
    
    return True

def main():
    """Run migrations on all databases"""
    print("🔧 Database Schema Standardization")
    print("=" * 50)
    
    # Define databases to migrate
    databases = [
        ("Dev SQLite", "core_app/real_estate_crm.db"),
        ("Dev Docker", "dev_crm.db"),
        ("Staging Docker", "staging_data/staging_crm.db"),
        ("Original", "real_estate_crm.db"),
    ]
    
    success_count = 0
    for name, path in databases:
        if migrate_database(path):
            success_count += 1
    
    print(f"\n✅ Successfully migrated {success_count}/{len(databases)} databases")
    
    # Also create a migration for Docker containers
    print("\n📝 Creating Docker migration script...")
    with open("migrate_docker_db.sh", "w") as f:
        f.write("""#!/bin/bash
# Run migrations inside Docker containers

echo "🐳 Migrating Docker databases..."

# Dev container
if docker ps | grep -q offer-creator-dev; then
    echo "Migrating dev container..."
    docker cp scripts/standardize-schema.py offer-creator-dev:/tmp/
    docker exec offer-creator-dev python /tmp/standardize-schema.py
fi

# Staging container  
if docker ps | grep -q offer-creator-staging; then
    echo "Migrating staging container..."
    docker cp scripts/standardize-schema.py offer-creator-staging:/tmp/
    docker exec offer-creator-staging python /tmp/standardize-schema.py
fi

echo "✅ Docker migrations complete"
""")
    os.chmod("migrate_docker_db.sh", 0o755)
    print("✅ Created migrate_docker_db.sh")

if __name__ == "__main__":
    main()