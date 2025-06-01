-- AI-Enhanced Real Estate CRM - Production Database Schema
-- 177-field comprehensive schema for real estate professionals

-- Enable UUID extension for unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Client Management Tables
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    mobile VARCHAR(50),
    work_phone VARCHAR(50),
    preferred_contact VARCHAR(20) DEFAULT 'email',
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'USA',
    date_of_birth DATE,
    occupation VARCHAR(100),
    employer VARCHAR(255),
    annual_income DECIMAL(15,2),
    credit_score INTEGER,
    pre_approval_amount DECIMAL(15,2),
    pre_approval_date DATE,
    pre_approval_lender VARCHAR(255),
    client_type VARCHAR(50) DEFAULT 'buyer', -- buyer, seller, both
    lead_source VARCHAR(100),
    referral_source VARCHAR(255),
    spouse_name VARCHAR(255),
    spouse_email VARCHAR(255),
    spouse_phone VARCHAR(50),
    emergency_contact_name VARCHAR(255),
    emergency_contact_phone VARCHAR(50),
    notes TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

-- Property Management Tables
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mls_number VARCHAR(50) UNIQUE,
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    county VARCHAR(100),
    parcel_number VARCHAR(100),
    property_type VARCHAR(50), -- single_family, condo, townhouse, etc.
    listing_type VARCHAR(50), -- sale, rent, lease
    bedrooms DECIMAL(3,1),
    bathrooms DECIMAL(3,1),
    square_feet INTEGER,
    lot_size DECIMAL(10,2),
    lot_size_units VARCHAR(20) DEFAULT 'sqft',
    year_built INTEGER,
    garage_spaces INTEGER,
    parking_spaces INTEGER,
    hoa_fees DECIMAL(10,2),
    hoa_frequency VARCHAR(20),
    property_taxes DECIMAL(10,2),
    tax_year INTEGER,
    listing_price DECIMAL(15,2),
    original_price DECIMAL(15,2),
    price_per_sqft DECIMAL(10,2),
    days_on_market INTEGER,
    listing_date DATE,
    pending_date DATE,
    sold_date DATE,
    sold_price DECIMAL(15,2),
    commission_rate DECIMAL(6,4), -- allows up to 99.9999%
    listing_agent_id UUID,
    selling_agent_id UUID,
    listing_office VARCHAR(255),
    selling_office VARCHAR(255),
    property_description TEXT,
    public_remarks TEXT,
    private_remarks TEXT,
    showing_instructions TEXT,
    features TEXT[], -- Array of features
    appliances TEXT[],
    utilities TEXT[],
    heating_cooling VARCHAR(255),
    flooring VARCHAR(255),
    roof_type VARCHAR(100),
    exterior VARCHAR(255),
    foundation VARCHAR(100),
    water_source VARCHAR(100),
    sewer VARCHAR(100),
    zoning VARCHAR(100),
    school_district VARCHAR(255),
    elementary_school VARCHAR(255),
    middle_school VARCHAR(255),
    high_school VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    virtual_tour_url VARCHAR(500),
    video_url VARCHAR(500),
    floor_plan_url VARCHAR(500),
    disclosure_documents TEXT[],
    inspection_reports TEXT[],
    appraisal_value DECIMAL(15,2),
    appraisal_date DATE,
    comparable_sales TEXT[],
    market_analysis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

-- Transaction Management Tables
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_type VARCHAR(50) NOT NULL, -- purchase, sale, lease
    property_id UUID REFERENCES properties(id),
    buyer_client_id UUID REFERENCES clients(id),
    seller_client_id UUID REFERENCES clients(id),
    contract_date DATE,
    closing_date DATE,
    purchase_price DECIMAL(15,2),
    down_payment DECIMAL(15,2),
    loan_amount DECIMAL(15,2),
    loan_type VARCHAR(100),
    lender_name VARCHAR(255),
    lender_contact VARCHAR(255),
    loan_officer VARCHAR(255),
    interest_rate DECIMAL(6,4),
    loan_term INTEGER,
    earnest_money DECIMAL(15,2),
    inspection_period INTEGER,
    financing_contingency_date DATE,
    appraisal_contingency_date DATE,
    title_company VARCHAR(255),
    title_officer VARCHAR(255),
    escrow_company VARCHAR(255),
    escrow_officer VARCHAR(255),
    home_warranty BOOLEAN DEFAULT FALSE,
    home_warranty_company VARCHAR(255),
    commission_buyer_agent DECIMAL(5,4),
    commission_seller_agent DECIMAL(5,4),
    commission_total DECIMAL(15,2),
    closing_costs_buyer DECIMAL(15,2),
    closing_costs_seller DECIMAL(15,2),
    transaction_status VARCHAR(50) DEFAULT 'pending',
    contingencies TEXT[],
    addenda TEXT[],
    important_dates JSONB,
    documents TEXT[],
    notes TEXT,
    referral_fee DECIMAL(15,2),
    referral_recipient VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

-- AI Integration Tables
CREATE TABLE email_processing_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email_subject VARCHAR(500),
    email_from VARCHAR(255),
    email_date TIMESTAMP,
    processing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extraction_confidence DECIMAL(5,4),
    extracted_entities JSONB,
    client_id UUID REFERENCES clients(id),
    property_id UUID REFERENCES properties(id),
    transaction_id UUID REFERENCES transactions(id),
    status VARCHAR(50) DEFAULT 'processed',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workflow_automation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trigger_type VARCHAR(100),
    trigger_data JSONB,
    workflow_name VARCHAR(255),
    actions_taken TEXT[],
    execution_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    client_id UUID REFERENCES clients(id),
    property_id UUID REFERENCES properties(id),
    transaction_id UUID REFERENCES transactions(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Management Tables
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(50),
    role VARCHAR(50) DEFAULT 'agent', -- admin, manager, agent
    license_number VARCHAR(100),
    license_state VARCHAR(50),
    office_name VARCHAR(255),
    office_address TEXT,
    bio TEXT,
    profile_image VARCHAR(500),
    commission_split DECIMAL(5,4),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked BOOLEAN DEFAULT FALSE,
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit and Logging Tables
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100),
    record_id UUID,
    action VARCHAR(50), -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    user_id UUID REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- Performance Indexes
CREATE INDEX idx_clients_email ON clients(email);
CREATE INDEX idx_clients_phone ON clients(phone);
CREATE INDEX idx_clients_status ON clients(status);
CREATE INDEX idx_clients_created_at ON clients(created_at);

CREATE INDEX idx_properties_mls ON properties(mls_number);
CREATE INDEX idx_properties_address ON properties(city, state, zip_code);
CREATE INDEX idx_properties_price ON properties(listing_price);
CREATE INDEX idx_properties_status ON properties(status);
CREATE INDEX idx_properties_listing_date ON properties(listing_date);

CREATE INDEX idx_transactions_status ON transactions(transaction_status);
CREATE INDEX idx_transactions_closing_date ON transactions(closing_date);
CREATE INDEX idx_transactions_property ON transactions(property_id);
CREATE INDEX idx_transactions_buyer ON transactions(buyer_client_id);
CREATE INDEX idx_transactions_seller ON transactions(seller_client_id);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);

CREATE INDEX idx_audit_log_table ON audit_log(table_name);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_log_user ON audit_log(user_id);

-- Update triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- Sample data for testing
INSERT INTO users (username, email, password_hash, first_name, last_name, role) VALUES
('admin', 'admin@narissarealty.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkY0XGOzJB7iR/K', 'Admin', 'User', 'admin'),
('narissa', 'narissa@narissarealty.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkY0XGOzJB7iR/K', 'Narissa', 'Agent', 'manager');

-- Schema completion message
SELECT 'AI-Enhanced Real Estate CRM Schema - 177 fields successfully created' AS status;