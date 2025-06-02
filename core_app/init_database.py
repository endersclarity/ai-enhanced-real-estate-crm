#!/usr/bin/env python3
"""
Initialize SQLite database for Real Estate CRM
Converts PostgreSQL schema to SQLite-compatible format
"""

import sqlite3
import os
from datetime import datetime

DATABASE_PATH = '../real_estate_crm.db'

# SQLite-compatible schema based on the original PostgreSQL schema
SQLITE_SCHEMA = """
-- AI-Enhanced Real Estate CRM - SQLite Database Schema
-- 177-field comprehensive schema for real estate professionals

-- Client Management Table
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    middle_initial VARCHAR(5),
    email VARCHAR(255) UNIQUE,
    home_phone VARCHAR(50),
    business_phone VARCHAR(50),
    cellular_phone VARCHAR(50),
    fax_number VARCHAR(50),
    preferred_contact_method VARCHAR(20) DEFAULT 'email',
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    county VARCHAR(100),
    country VARCHAR(100) DEFAULT 'USA',
    date_of_birth DATE,
    occupation VARCHAR(100),
    employer VARCHAR(255),
    annual_income DECIMAL(15,2),
    credit_score INTEGER,
    pre_approval_amount DECIMAL(15,2),
    pre_approval_date DATE,
    pre_approval_lender VARCHAR(255),
    client_type VARCHAR(50) DEFAULT 'buyer',
    lead_source VARCHAR(100),
    referral_source VARCHAR(255),
    spouse_name VARCHAR(255),
    spouse_email VARCHAR(255),
    spouse_phone VARCHAR(50),
    emergency_contact_name VARCHAR(255),
    emergency_contact_phone VARCHAR(50),
    ssn_last_four VARCHAR(4),
    notes TEXT,
    auto_signature_enabled BOOLEAN DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Property Management Table
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mls_number VARCHAR(50) UNIQUE,
    street_address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    county VARCHAR(100),
    township VARCHAR(100),
    legal_description TEXT,
    tax_id VARCHAR(100),
    assessor_parcel_number VARCHAR(100),
    lot_number VARCHAR(50),
    unit_number VARCHAR(50),
    block VARCHAR(50),
    subdivision VARCHAR(100),
    plat_book VARCHAR(50),
    page_number VARCHAR(50),
    listing_date DATE,
    expiration_date DATE,
    listed_price DECIMAL(15,2),
    original_price DECIMAL(15,2),
    property_type VARCHAR(50) DEFAULT 'Residential',
    year_built INTEGER,
    bedrooms INTEGER,
    bathrooms DECIMAL(3,1),
    square_feet INTEGER,
    lot_size_acres DECIMAL(10,4),
    lot_size_sqft INTEGER,
    mobile_home_year INTEGER,
    mobile_home_make VARCHAR(100),
    mobile_home_serial_number VARCHAR(100),
    mobile_home_hcd_decal VARCHAR(100),
    balance_first_mortgage DECIMAL(15,2),
    balance_second_mortgage DECIMAL(15,2),
    other_liens DECIMAL(15,2),
    other_liens_description TEXT,
    total_encumbrances DECIMAL(15,2),
    homeowner_assoc_dues DECIMAL(10,2),
    transfer_fee DECIMAL(10,2),
    doc_prep_fees DECIMAL(10,2),
    property_includes TEXT,
    property_excludes TEXT,
    leased_items TEXT,
    supplemental_info TEXT,
    purchase_price DECIMAL(15,2),
    purchase_agreement_date DATE,
    closing_date DATE,
    deposit_amount DECIMAL(15,2),
    deposit_amount_1st_increase DECIMAL(15,2),
    deposit_amount_2nd_increase DECIMAL(15,2),
    deposit_amount_3rd_increase DECIMAL(15,2),
    offer_date DATE,
    expire_date DATE,
    expire_time TIME,
    offer_acceptance_date DATE,
    total_amount_financed DECIMAL(15,2),
    property_description TEXT,
    public_remarks TEXT,
    private_remarks TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transaction Management Table
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_type VARCHAR(50) NOT NULL, -- purchase, sale, lease
    property_id INTEGER NOT NULL,
    buyer_client_id INTEGER,
    seller_client_id INTEGER,
    purchase_price DECIMAL(15,2),
    original_offer_price DECIMAL(15,2),
    final_sale_price DECIMAL(15,2),
    offer_date DATE,
    offer_expiration_date DATE,
    offer_expiration_time TIME,
    acceptance_date DATE,
    contract_date DATE,
    closing_date DATE,
    down_payment_amount DECIMAL(15,2),
    down_payment_percentage DECIMAL(5,2),
    loan_amount DECIMAL(15,2),
    loan_term_years INTEGER,
    interest_rate DECIMAL(6,4),
    total_amount_financed DECIMAL(15,2),
    earnest_money_amount DECIMAL(15,2),
    deposit_amount DECIMAL(15,2),
    deposit_1st_increase DECIMAL(15,2),
    deposit_2nd_increase DECIMAL(15,2),
    deposit_3rd_increase DECIMAL(15,2),
    listing_broker_id INTEGER,
    selling_broker_id INTEGER,
    listing_agent_id INTEGER,
    selling_agent_id INTEGER,
    lender_id INTEGER,
    title_company_id INTEGER,
    escrow_company_id INTEGER,
    appraisal_company_id INTEGER,
    pest_control_providers TEXT,
    disclosure_providers TEXT,
    home_warranty_providers TEXT,
    hoa_providers TEXT,
    transaction_coordinators TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    financing_contingency_date DATE,
    inspection_contingency_date DATE,
    appraisal_contingency_date DATE,
    title_contingency_date DATE,
    sale_of_property_contingency_date DATE,
    homeowners_insurance_contingency_date DATE,
    hoa_approval_contingency_date DATE,
    as_is_sale BOOLEAN DEFAULT 0,
    seller_financing BOOLEAN DEFAULT 0,
    home_warranty BOOLEAN DEFAULT 0,
    notes TEXT,
    private_remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id),
    FOREIGN KEY (buyer_client_id) REFERENCES clients(id),
    FOREIGN KEY (seller_client_id) REFERENCES clients(id)
);

-- Broker/Agent Management Table
CREATE TABLE IF NOT EXISTS brokers_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_name VARCHAR(255) NOT NULL,
    firm_address VARCHAR(255),
    firm_city VARCHAR(100),
    firm_state VARCHAR(50),
    firm_zip_code VARCHAR(20),
    firm_phone VARCHAR(50),
    firm_dre_license VARCHAR(100),
    agent_name VARCHAR(255) NOT NULL,
    agent_phone VARCHAR(50),
    agent_cellular VARCHAR(50),
    agent_fax VARCHAR(50),
    agent_email VARCHAR(255),
    agent_dre_license VARCHAR(100),
    role VARCHAR(50) NOT NULL, -- listing_office, selling_office, listing_agent, selling_agent
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lender Management Table
CREATE TABLE IF NOT EXISTS lenders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name VARCHAR(255) NOT NULL,
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    phone VARCHAR(50),
    fax VARCHAR(50),
    officer_name VARCHAR(255),
    officer_cell_phone VARCHAR(50),
    officer_email VARCHAR(255),
    mortgage_type VARCHAR(100),
    mortgage_type_other VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Title Company Management Table
CREATE TABLE IF NOT EXISTS title_companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name VARCHAR(255) NOT NULL,
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    phone VARCHAR(50),
    fax VARCHAR(50),
    officer_name VARCHAR(255),
    officer_cell_phone VARCHAR(50),
    officer_email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Escrow Company Management Table
CREATE TABLE IF NOT EXISTS escrow_companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name VARCHAR(255) NOT NULL,
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    phone VARCHAR(50),
    fax VARCHAR(50),
    officer_name VARCHAR(255),
    officer_license_number VARCHAR(100),
    officer_email VARCHAR(255),
    escrow_number VARCHAR(100),
    closing_date DATE,
    deposit_one DECIMAL(15,2),
    deposit_two DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service Provider Management Table
CREATE TABLE IF NOT EXISTS service_providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name VARCHAR(255) NOT NULL,
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    phone VARCHAR(50),
    fax VARCHAR(50),
    representative_name VARCHAR(255),
    representative_cell_phone VARCHAR(50),
    representative_email VARCHAR(255),
    service_type VARCHAR(100) NOT NULL, -- pest_control, disclosure, home_warranty, hoa, transaction_coordinator
    coordinator_side VARCHAR(50), -- buyer, seller, both
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Offer Creation Workflow Table
CREATE TABLE IF NOT EXISTS offers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id VARCHAR(100) UNIQUE NOT NULL,
    form_type VARCHAR(50) NOT NULL,
    buyer_client_id INTEGER NOT NULL,
    property_id INTEGER NOT NULL,
    agent_id INTEGER,
    lender_id INTEGER,
    offer_terms TEXT, -- JSON blob of offer terms
    status VARCHAR(50) DEFAULT 'draft', -- draft, review, approved, sent, accepted, rejected
    pdf_path VARCHAR(500),
    transaction_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_client_id) REFERENCES clients(id),
    FOREIGN KEY (property_id) REFERENCES properties(id),
    FOREIGN KEY (agent_id) REFERENCES brokers_agents(id),
    FOREIGN KEY (lender_id) REFERENCES lenders(id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);
"""

def initialize_database():
    """Initialize the SQLite database with the complete schema"""
    try:
        # Check if database file exists
        db_exists = os.path.exists(DATABASE_PATH)
        
        # Connect to database (creates file if it doesn't exist)
        conn = sqlite3.connect(DATABASE_PATH)
        
        # Execute schema creation
        conn.executescript(SQLITE_SCHEMA)
        conn.commit()
        
        print(f"✅ Database initialized successfully at {DATABASE_PATH}")
        
        # Check created tables
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def insert_sample_data():
    """Insert sample data for testing offer creation"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        
        # Sample client
        conn.execute("""
            INSERT OR IGNORE INTO clients (
                first_name, last_name, email, cellular_phone, 
                street_address, city, state, zip_code, client_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "John", "Smith", "john.smith@email.com", "555-123-4567",
            "123 Buyer Lane", "Sacramento", "CA", "95814", "buyer"
        ))
        
        # Sample property
        conn.execute("""
            INSERT OR IGNORE INTO properties (
                street_address, city, state, zip_code, listed_price,
                bedrooms, bathrooms, square_feet, property_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "456 Main Street", "Sacramento", "CA", "95814", 500000,
            3, 2.0, 1500, "Residential"
        ))
        
        # Sample agent
        conn.execute("""
            INSERT OR IGNORE INTO brokers_agents (
                firm_name, agent_name, agent_phone, agent_email, role
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            "Narissa Realty", "Narissa Agent", "555-999-8888", "narissa@realty.com", "selling_agent"
        ))
        
        # Sample lender
        conn.execute("""
            INSERT OR IGNORE INTO lenders (
                company_name, officer_name, phone, mortgage_type
            ) VALUES (?, ?, ?, ?)
        """, (
            "First Bank Lending", "Jane Banker", "555-777-6666", "Conv"
        ))
        
        conn.commit()
        conn.close()
        
        print("✅ Sample data inserted successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")
        return False

if __name__ == "__main__":
    print("🏗️ Initializing Real Estate CRM Database")
    print("=" * 50)
    
    # Initialize database
    if initialize_database():
        print("\n📝 Inserting sample data...")
        insert_sample_data()
        print("\n🎉 Database setup complete!")
        print(f"\nDatabase location: {os.path.abspath(DATABASE_PATH)}")
    else:
        print("\n❌ Database initialization failed")