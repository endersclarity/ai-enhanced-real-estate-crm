#!/usr/bin/env python3
"""
Database Migration Script for ZipForm Compatibility
Safely migrates existing real_estate_crm.db to comprehensive ZipForm schema
"""

import sqlite3
import os
import json
from datetime import datetime

DATABASE_PATH = 'real_estate_crm.db'
BACKUP_PATH = f'real_estate_crm_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
SCHEMA_PATH = 'zipform_enhanced_schema.sql'

def backup_database():
    """Create a backup of the existing database"""
    if os.path.exists(DATABASE_PATH):
        import shutil
        shutil.copy2(DATABASE_PATH, BACKUP_PATH)
        print(f"✅ Database backed up to: {BACKUP_PATH}")
        return True
    else:
        print("ℹ️  No existing database found - creating fresh database")
        return False

def migrate_existing_data():
    """Migrate existing client and property data to new schema"""
    
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    migration_log = {
        'timestamp': datetime.now().isoformat(),
        'clients_migrated': 0,
        'properties_migrated': 0,
        'errors': []
    }
    
    try:
        # Check if old tables exist
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = [table['name'] for table in tables]
        
        print(f"📋 Found existing tables: {table_names}")
        
        # Migrate clients data if old clients table exists
        if 'clients' in table_names:
            print("🔄 Migrating clients data...")
            
            # Get existing clients
            old_clients = cursor.execute("SELECT * FROM clients").fetchall()
            
            # Rename old table
            cursor.execute("ALTER TABLE clients RENAME TO clients_old")
            
            # Create new clients table structure (from schema)
            cursor.execute('''
                CREATE TABLE clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    middle_initial TEXT,
                    email TEXT UNIQUE,
                    home_phone TEXT,
                    business_phone TEXT,
                    cellular_phone TEXT,
                    fax_number TEXT,
                    preferred_contact_method TEXT DEFAULT 'email',
                    street_address TEXT,
                    city TEXT,
                    state TEXT,
                    zip_code TEXT,
                    county TEXT,
                    client_type TEXT DEFAULT 'buyer',
                    employer TEXT,
                    occupation TEXT,
                    annual_income REAL,
                    ssn_last_four TEXT,
                    notes TEXT,
                    auto_signature_enabled BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Migrate data with field mapping
            for client in old_clients:
                try:
                    cursor.execute('''
                        INSERT INTO clients (
                            id, first_name, last_name, email, home_phone, 
                            preferred_contact_method, street_address, city, state, zip_code,
                            client_type, employer, occupation, annual_income, ssn_last_four,
                            notes, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        client['id'], client['first_name'], client['last_name'], 
                        client['email'], client['phone_primary'], 
                        client.get('preferred_contact_method', 'email'),
                        client.get('address_street'), client.get('address_city'), 
                        client.get('address_state'), client.get('address_zip'),
                        client.get('client_type', 'buyer'), client.get('employer'),
                        client.get('occupation'), client.get('annual_income'),
                        client.get('ssn_last_four'), client.get('notes'),
                        client.get('created_at')
                    ))
                    migration_log['clients_migrated'] += 1
                except Exception as e:
                    migration_log['errors'].append(f"Client migration error: {str(e)}")
            
            print(f"✅ Migrated {migration_log['clients_migrated']} clients")
        
        # Migrate properties data if old properties table exists
        if 'properties' in table_names:
            print("🔄 Migrating properties data...")
            
            # Get existing properties
            old_properties = cursor.execute("SELECT * FROM properties").fetchall()
            
            # Rename old table
            cursor.execute("ALTER TABLE properties RENAME TO properties_old")
            
            # Create new properties table structure (from schema)
            cursor.execute('''
                CREATE TABLE properties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    street_address TEXT NOT NULL,
                    city TEXT NOT NULL,
                    state TEXT NOT NULL,
                    zip_code TEXT NOT NULL,
                    county TEXT,
                    township TEXT,
                    legal_description TEXT,
                    tax_id TEXT,
                    assessor_parcel_number TEXT,
                    lot_number TEXT,
                    unit_number TEXT,
                    block TEXT,
                    subdivision TEXT,
                    plat_book TEXT,
                    page_number TEXT,
                    mls_number TEXT UNIQUE,
                    listing_date DATE,
                    expiration_date DATE,
                    listed_price REAL,
                    original_price REAL,
                    property_type TEXT DEFAULT 'Residential',
                    year_built INTEGER,
                    bedrooms REAL,
                    bathrooms REAL,
                    square_feet INTEGER,
                    lot_size_acres REAL,
                    lot_size_sqft INTEGER,
                    mobile_home_year INTEGER,
                    mobile_home_make TEXT,
                    mobile_home_serial_number TEXT,
                    mobile_home_hcd_decal TEXT,
                    balance_first_mortgage REAL,
                    balance_second_mortgage REAL,
                    other_liens REAL,
                    other_liens_description TEXT,
                    total_encumbrances REAL,
                    homeowner_assoc_dues REAL,
                    transfer_fee REAL,
                    doc_prep_fees REAL,
                    property_includes TEXT,
                    property_excludes TEXT,
                    leased_items TEXT,
                    supplemental_info TEXT,
                    purchase_price REAL,
                    purchase_agreement_date DATE,
                    closing_date DATE,
                    deposit_amount REAL,
                    deposit_amount_1st_increase REAL,
                    deposit_amount_2nd_increase REAL,
                    deposit_amount_3rd_increase REAL,
                    offer_date DATE,
                    expire_date DATE,
                    expire_time TEXT,
                    offer_acceptance_date DATE,
                    total_amount_financed REAL,
                    property_description TEXT,
                    public_remarks TEXT,
                    private_remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Migrate data with field mapping
            for prop in old_properties:
                try:
                    cursor.execute('''
                        INSERT INTO properties (
                            id, street_address, city, state, zip_code, mls_number,
                            property_type, bedrooms, bathrooms, square_feet, lot_size_acres,
                            year_built, listed_price, property_description, public_remarks,
                            private_remarks, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        prop['id'], prop['address_line1'], prop['city'], prop['state'],
                        prop['zip_code'], prop.get('mls_number'), 
                        prop.get('property_type', 'Residential'), prop.get('bedrooms'),
                        prop.get('bathrooms'), prop.get('square_feet'), prop.get('lot_size'),
                        prop.get('year_built'), prop.get('listing_price'),
                        prop.get('property_description'), prop.get('public_remarks'),
                        prop.get('private_remarks'), prop.get('created_at')
                    ))
                    migration_log['properties_migrated'] += 1
                except Exception as e:
                    migration_log['errors'].append(f"Property migration error: {str(e)}")
            
            print(f"✅ Migrated {migration_log['properties_migrated']} properties")
        
        conn.commit()
        
    except Exception as e:
        migration_log['errors'].append(f"Migration error: {str(e)}")
        conn.rollback()
        print(f"❌ Migration error: {str(e)}")
        raise
    
    finally:
        conn.close()
    
    return migration_log

def create_new_tables():
    """Create new tables for ZipForm functionality"""
    print("🔄 Creating new ZipForm tables...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Read and execute the comprehensive schema
        with open(SCHEMA_PATH, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema in parts (SQLite doesn't handle multiple statements well)
        statements = schema_sql.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                except sqlite3.Error as e:
                    if "already exists" not in str(e):
                        print(f"⚠️  Schema execution warning: {e}")
        
        conn.commit()
        print("✅ New ZipForm tables created successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating new tables: {str(e)}")
        raise
    
    finally:
        conn.close()

def verify_migration():
    """Verify the migration was successful"""
    print("🔍 Verifying migration...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Check all expected tables exist
        expected_tables = [
            'clients', 'properties', 'transactions', 'brokers_agents',
            'lenders', 'title_companies', 'escrow_companies', 
            'appraisal_companies', 'service_providers'
        ]
        
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        existing_tables = [table[0] for table in tables]
        
        print(f"📋 Found tables: {existing_tables}")
        
        for table in expected_tables:
            if table in existing_tables:
                count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                print(f"  ✅ {table}: {count} records")
            else:
                print(f"  ❌ Missing table: {table}")
        
        # Check data preservation
        clients_count = cursor.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
        properties_count = cursor.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
        
        print(f"\n📊 Migration Summary:")
        print(f"  • Clients preserved: {clients_count}")
        print(f"  • Properties preserved: {properties_count}")
        print(f"  • New ZipForm tables: {len([t for t in expected_tables if t not in ['clients', 'properties']])}")
        
    except Exception as e:
        print(f"❌ Verification error: {str(e)}")
        raise
    
    finally:
        conn.close()

def main():
    """Main migration process"""
    print("🚀 Starting ZipForm Database Migration")
    print("=" * 60)
    
    try:
        # Step 1: Backup existing database
        had_existing_db = backup_database()
        
        # Step 2: Create new schema structure
        create_new_tables()
        
        # Step 3: Migrate existing data if we had a database
        if had_existing_db:
            migration_log = migrate_existing_data()
            
            # Save migration log
            with open(f'migration_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
                json.dump(migration_log, f, indent=2)
        
        # Step 4: Verify migration
        verify_migration()
        
        print("\n🎉 Migration completed successfully!")
        print("Your database now supports all ZipForm Transaction Cover Sheet fields")
        
        if had_existing_db:
            print(f"📁 Original database backed up to: {BACKUP_PATH}")
        
    except Exception as e:
        print(f"\n💥 Migration failed: {str(e)}")
        if had_existing_db and os.path.exists(BACKUP_PATH):
            print(f"🔄 Restore from backup: {BACKUP_PATH}")
        raise

if __name__ == "__main__":
    main()