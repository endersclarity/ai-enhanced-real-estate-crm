-- ZipForm-Compatible Real Estate CRM Schema (SQLite)
-- Comprehensive schema covering all ZipForm Transaction Cover Sheet fields
-- Date: 2025-01-31

PRAGMA foreign_keys = ON;

-- ============================================================================
-- EXPANDED CLIENTS TABLE (Buyer/Seller Information)
-- ============================================================================
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Basic Information
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    middle_initial TEXT,
    
    -- Contact Information (ZipForm fields)
    email TEXT UNIQUE,
    home_phone TEXT,
    business_phone TEXT,
    cellular_phone TEXT,
    fax_number TEXT,
    preferred_contact_method TEXT DEFAULT 'email',
    
    -- Address Information
    street_address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    county TEXT,
    
    -- Client Classification
    client_type TEXT DEFAULT 'buyer', -- buyer, seller, both
    
    -- Additional Information
    employer TEXT,
    occupation TEXT,
    annual_income REAL,
    ssn_last_four TEXT,
    notes TEXT,
    
    -- Auto-signature preference (ZipForm feature)
    auto_signature_enabled BOOLEAN DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- EXPANDED PROPERTIES TABLE (Property Information)
-- ============================================================================
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Basic Address
    street_address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    county TEXT,
    township TEXT,
    
    -- Legal Information
    legal_description TEXT,
    tax_id TEXT,
    assessor_parcel_number TEXT,
    lot_number TEXT,
    unit_number TEXT,
    block TEXT,
    subdivision TEXT,
    plat_book TEXT,
    page_number TEXT,
    
    -- MLS Information
    mls_number TEXT UNIQUE,
    listing_date DATE,
    expiration_date DATE,
    listed_price REAL,
    original_price REAL,
    
    -- Property Details
    property_type TEXT DEFAULT 'Residential', -- Residential, Multi Family, Vacant Land, Commercial, Other
    year_built INTEGER,
    bedrooms REAL,
    bathrooms REAL,
    square_feet INTEGER,
    lot_size_acres REAL,
    lot_size_sqft INTEGER,
    
    -- Mobile Home Details (ZipForm specific)
    mobile_home_year INTEGER,
    mobile_home_make TEXT,
    mobile_home_serial_number TEXT,
    mobile_home_hcd_decal TEXT,
    
    -- Financial Information
    balance_first_mortgage REAL,
    balance_second_mortgage REAL,
    other_liens REAL,
    other_liens_description TEXT,
    total_encumbrances REAL,
    homeowner_assoc_dues REAL,
    transfer_fee REAL,
    doc_prep_fees REAL,
    
    -- Property Features
    property_includes TEXT,
    property_excludes TEXT,
    leased_items TEXT,
    supplemental_info TEXT,
    
    -- Transaction Information
    purchase_price REAL,
    purchase_agreement_date DATE,
    closing_date DATE,
    
    -- Deposit Information
    deposit_amount REAL,
    deposit_amount_1st_increase REAL,
    deposit_amount_2nd_increase REAL,
    deposit_amount_3rd_increase REAL,
    
    -- Offer Information
    offer_date DATE,
    expire_date DATE,
    expire_time TEXT, -- Store as "HH:MM AM/PM"
    offer_acceptance_date DATE,
    total_amount_financed REAL,
    
    -- Descriptions
    property_description TEXT,
    public_remarks TEXT,
    private_remarks TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- BROKERS AND AGENTS TABLE (Buyer's/Seller's Broker Information)
-- ============================================================================
CREATE TABLE IF NOT EXISTS brokers_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Firm Information
    firm_name TEXT NOT NULL,
    firm_address TEXT,
    firm_city TEXT,
    firm_state TEXT,
    firm_zip_code TEXT,
    firm_phone TEXT,
    firm_dre_license TEXT,
    
    -- Agent Information
    agent_name TEXT NOT NULL,
    agent_phone TEXT,
    agent_cellular TEXT,
    agent_fax TEXT,
    agent_email TEXT,
    agent_dre_license TEXT,
    
    -- Role Classification
    role TEXT NOT NULL, -- 'listing_office', 'selling_office', 'listing_agent', 'selling_agent'
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- LENDER INFORMATION TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS lenders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Company Information
    company_name TEXT NOT NULL,
    street_address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    phone TEXT,
    fax TEXT,
    
    -- Officer Information
    officer_name TEXT,
    officer_cell_phone TEXT,
    officer_email TEXT,
    
    -- Loan Type
    mortgage_type TEXT, -- Conv, FHA, FMHA, VA, Other
    mortgage_type_other TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TITLE COMPANY INFORMATION TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS title_companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Company Information
    company_name TEXT NOT NULL,
    street_address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    phone TEXT,
    fax TEXT,
    
    -- Officer Information
    officer_name TEXT,
    officer_cell_phone TEXT,
    officer_email TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ESCROW COMPANY INFORMATION TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS escrow_companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Company Information
    company_name TEXT NOT NULL,
    street_address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    phone TEXT,
    fax TEXT,
    
    -- Officer Information
    officer_name TEXT,
    officer_license_number TEXT,
    officer_email TEXT,
    
    -- Escrow Details
    escrow_number TEXT,
    closing_date DATE,
    deposit_one DATE,
    deposit_two DATE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- APPRAISAL COMPANY INFORMATION TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS appraisal_companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Company Information
    company_name TEXT NOT NULL,
    street_address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    phone TEXT,
    fax TEXT,
    
    -- Officer Information
    officer_name TEXT,
    officer_cell_phone TEXT,
    officer_email TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SERVICE PROVIDERS TABLE (Pest Control, Disclosure, Home Warranty, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS service_providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Company Information
    company_name TEXT NOT NULL,
    street_address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    phone TEXT,
    fax TEXT,
    
    -- Representative Information
    representative_name TEXT,
    representative_cell_phone TEXT,
    representative_email TEXT,
    
    -- Service Type
    service_type TEXT NOT NULL, -- 'pest_control', 'disclosure', 'home_warranty', 'hoa', 'transaction_coordinator'
    
    -- Transaction Coordinator specific fields
    coordinator_side TEXT, -- 'buy_side', 'sell_side' (for transaction coordinators)
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- COMPREHENSIVE TRANSACTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Core Transaction Information
    transaction_type TEXT NOT NULL, -- purchase, sale, lease
    property_id INTEGER REFERENCES properties(id),
    buyer_client_id INTEGER REFERENCES clients(id),
    seller_client_id INTEGER REFERENCES clients(id),
    
    -- Pricing Information
    purchase_price REAL,
    original_offer_price REAL,
    final_sale_price REAL,
    
    -- Important Dates
    offer_date DATE,
    offer_expiration_date DATE,
    offer_expiration_time TEXT,
    acceptance_date DATE,
    contract_date DATE,
    closing_date DATE,
    
    -- Financing Information
    down_payment_amount REAL,
    down_payment_percentage REAL,
    loan_amount REAL,
    loan_term_years INTEGER,
    interest_rate REAL,
    total_amount_financed REAL,
    
    -- Deposit Information
    earnest_money_amount REAL,
    deposit_amount REAL,
    deposit_1st_increase REAL,
    deposit_2nd_increase REAL,
    deposit_3rd_increase REAL,
    
    -- Service Provider Relationships
    listing_broker_id INTEGER REFERENCES brokers_agents(id),
    selling_broker_id INTEGER REFERENCES brokers_agents(id),
    listing_agent_id INTEGER REFERENCES brokers_agents(id),
    selling_agent_id INTEGER REFERENCES brokers_agents(id),
    lender_id INTEGER REFERENCES lenders(id),
    title_company_id INTEGER REFERENCES title_companies(id),
    escrow_company_id INTEGER REFERENCES escrow_companies(id),
    appraisal_company_id INTEGER REFERENCES appraisal_companies(id),
    
    -- Service Providers (using JSON for multiple providers of same type)
    pest_control_providers TEXT, -- JSON array of service_provider IDs
    disclosure_providers TEXT,   -- JSON array of service_provider IDs
    home_warranty_providers TEXT, -- JSON array of service_provider IDs
    hoa_providers TEXT,          -- JSON array of service_provider IDs
    transaction_coordinators TEXT, -- JSON array of service_provider IDs
    
    -- Transaction Status
    status TEXT DEFAULT 'pending', -- pending, accepted, in_progress, closed, cancelled
    
    -- Contingencies and Important Dates
    financing_contingency_date DATE,
    inspection_contingency_date DATE,
    appraisal_contingency_date DATE,
    title_contingency_date DATE,
    sale_of_property_contingency_date DATE,
    homeowners_insurance_contingency_date DATE,
    hoa_approval_contingency_date DATE,
    
    -- Additional Transaction Details
    as_is_sale BOOLEAN DEFAULT 0,
    seller_financing BOOLEAN DEFAULT 0,
    home_warranty BOOLEAN DEFAULT 0,
    
    -- Notes and Comments
    notes TEXT,
    private_remarks TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Clients indexes
CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email);
CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_clients_phone ON clients(home_phone, cellular_phone, business_phone);
CREATE INDEX IF NOT EXISTS idx_clients_type ON clients(client_type);

-- Properties indexes
CREATE INDEX IF NOT EXISTS idx_properties_mls ON properties(mls_number);
CREATE INDEX IF NOT EXISTS idx_properties_address ON properties(city, state, zip_code);
CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(listed_price, purchase_price);
CREATE INDEX IF NOT EXISTS idx_properties_dates ON properties(listing_date, closing_date);

-- Transactions indexes
CREATE INDEX IF NOT EXISTS idx_transactions_property ON transactions(property_id);
CREATE INDEX IF NOT EXISTS idx_transactions_buyer ON transactions(buyer_client_id);
CREATE INDEX IF NOT EXISTS idx_transactions_seller ON transactions(seller_client_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_dates ON transactions(offer_date, closing_date);

-- Service provider indexes
CREATE INDEX IF NOT EXISTS idx_brokers_agents_role ON brokers_agents(role);
CREATE INDEX IF NOT EXISTS idx_service_providers_type ON service_providers(service_type);

-- ============================================================================
-- SAMPLE DATA FOR TESTING
-- ============================================================================

-- Insert sample broker/agent
INSERT OR IGNORE INTO brokers_agents (
    firm_name, firm_address, firm_city, firm_state, firm_zip_code, firm_phone,
    agent_name, agent_phone, agent_email, role
) VALUES (
    'Coldwell Banker Grass Roots Realty', 
    '167 South Auburn Street', 
    'Grass Valley', 
    'CA', 
    '95945',
    '(530) 276-5970',
    'Narissa Jennings',
    '(530) 276-5970',
    'narissa@cbgrr.com',
    'listing_agent'
);

-- Insert sample lender
INSERT OR IGNORE INTO lenders (
    company_name, phone, officer_name, mortgage_type
) VALUES (
    'Sample Mortgage Company',
    '(555) 123-4567',
    'John Loan Officer',
    'Conv'
);

-- Success message
SELECT 'ZipForm-Compatible Real Estate CRM Schema Created Successfully' AS status,
       'All ZipForm Transaction Cover Sheet fields are now supported' AS details;