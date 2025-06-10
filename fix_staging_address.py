#!/usr/bin/env python3
"""
Fix address column naming in staging
"""
import sqlite3
import os

db_path = os.environ.get('DATABASE_URL', 'sqlite:////app/data/staging_crm.db')
if db_path.startswith('sqlite:///'):
    db_path = db_path.replace('sqlite:///', '')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check what address columns exist
cursor.execute("PRAGMA table_info(properties)")
columns = {col[1]: col for col in cursor.fetchall()}

print("Current columns:", list(columns.keys())[:15])

# Copy address data to street_address if needed
if 'address' in columns and 'street_address' in columns:
    cursor.execute("UPDATE properties SET street_address = address WHERE street_address IS NULL")
    print("✓ Copied address → street_address")

# Add all missing transaction columns
transaction_columns = [
    'closing_cost_paid_by', 'personal_property_included', 'additional_terms',
    'contingency_removal_date', 'offer_expiration_date', 'possession_date',
    'home_warranty', 'home_warranty_provider', 'title_company',
    'escrow_company', 'attorney_name', 'broker_name', 'agent_name',
    'agent_license', 'broker_license', 'commission_percentage',
    'listing_agent_name', 'listing_agent_license', 'listing_broker_name',
    'listing_broker_license', 'mls_number', 'legal_description',
    'assessor_parcel_number', 'property_tax_amount', 'hoa_fee',
    'other_fees', 'rent_back_requested', 'rent_back_daily_rate',
    'seller_concessions_amount', 'repair_request_amount', 'as_is_sale',
    'seller_financing', 'assumable_loan', 'occupancy_status'
]

for col in transaction_columns:
    try:
        cursor.execute(f"ALTER TABLE transactions ADD COLUMN {col} TEXT")
        print(f"✓ Added transactions.{col}")
    except:
        pass  # Already exists

conn.commit()
print("\n✅ All address and transaction fixes applied!")
conn.close()