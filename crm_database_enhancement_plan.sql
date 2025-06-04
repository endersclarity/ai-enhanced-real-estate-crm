-- CRM Database Enhancement Plan for CAR Forms Integration
-- Adds essential fields needed to auto-populate the top 5 CAR forms

-- Enhanced Clients Table (additions to existing schema)
ALTER TABLE clients ADD COLUMN IF NOT EXISTS mobile_phone VARCHAR(20);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS work_phone VARCHAR(20);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS preferred_contact_method VARCHAR(20) DEFAULT 'phone';
ALTER TABLE clients ADD COLUMN IF NOT EXISTS spouse_name VARCHAR(100);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS spouse_email VARCHAR(100);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS spouse_phone VARCHAR(20);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS emergency_contact_name VARCHAR(100);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS emergency_contact_phone VARCHAR(20);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS emergency_contact_relationship VARCHAR(50);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS date_of_birth DATE;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS social_security_number VARCHAR(11);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS employer VARCHAR(100);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS occupation VARCHAR(100);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS annual_income DECIMAL(12,2);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS credit_score INTEGER;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS pre_approval_amount DECIMAL(12,2);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS pre_approval_date DATE;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS pre_approval_lender VARCHAR(100);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS client_type VARCHAR(20) DEFAULT 'buyer'; -- buyer, seller, both
ALTER TABLE clients ADD COLUMN IF NOT EXISTS lead_source VARCHAR(100);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS referral_source VARCHAR(100);

-- Enhanced Properties Table (additions to existing schema)
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mls_number VARCHAR(20);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS legal_description TEXT;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS apn VARCHAR(30); -- Assessor's Parcel Number
ALTER TABLE properties ADD COLUMN IF NOT EXISTS property_type VARCHAR(50); -- SFR, Condo, Townhouse, etc.
ALTER TABLE properties ADD COLUMN IF NOT EXISTS bedrooms INTEGER;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS bathrooms DECIMAL(3,1);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS square_feet INTEGER;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS lot_size VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS year_built INTEGER;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS listing_price DECIMAL(12,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS market_value DECIMAL(12,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS hoa_fees DECIMAL(8,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS property_taxes DECIMAL(10,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS special_assessments DECIMAL(10,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS garage_spaces INTEGER;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS parking_type VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS basement BOOLEAN DEFAULT FALSE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS fireplace BOOLEAN DEFAULT FALSE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS pool BOOLEAN DEFAULT FALSE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS listing_agent VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS listing_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS days_on_market INTEGER;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS price_per_sqft DECIMAL(8,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS property_condition VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS occupancy_status VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS school_district VARCHAR(100);

-- Enhanced Transactions Table (additions to existing schema) 
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS transaction_type VARCHAR(20) DEFAULT 'purchase'; -- purchase, sale, lease
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS purchase_price DECIMAL(12,2);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS earnest_money DECIMAL(10,2);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS down_payment DECIMAL(12,2);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS loan_amount DECIMAL(12,2);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS loan_type VARCHAR(50); -- conventional, FHA, VA, cash
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS interest_rate DECIMAL(5,3);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS monthly_payment DECIMAL(10,2);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS closing_date DATE;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS possession_date DATE;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS inspection_date DATE;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS appraisal_date DATE;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS contingency_date DATE;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS commission_rate DECIMAL(5,3);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS commission_amount DECIMAL(10,2);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS selling_agent VARCHAR(100);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS buyer_agent VARCHAR(100);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS escrow_company VARCHAR(100);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS title_company VARCHAR(100);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS lender VARCHAR(100);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS inspector VARCHAR(100);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS appraiser VARCHAR(100);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS transaction_coordinator VARCHAR(100);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS contract_date DATE;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS acceptance_date DATE;

-- Enhanced Agents Table (additions to existing schema)
ALTER TABLE agents ADD COLUMN IF NOT EXISTS license_number VARCHAR(20);
ALTER TABLE agents ADD COLUMN IF NOT EXISTS brokerage VARCHAR(100);
ALTER TABLE agents ADD COLUMN IF NOT EXISTS brokerage_address TEXT;
ALTER TABLE agents ADD COLUMN IF NOT EXISTS specialties TEXT;
ALTER TABLE agents ADD COLUMN IF NOT EXISTS commission_split DECIMAL(5,3);
ALTER TABLE agents ADD COLUMN IF NOT EXISTS years_experience INTEGER;
ALTER TABLE agents ADD COLUMN IF NOT EXISTS certifications TEXT;

-- New Table: Property Search Criteria (for Buyer Representation Agreement)
CREATE TABLE IF NOT EXISTS property_search_criteria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    min_price DECIMAL(12,2),
    max_price DECIMAL(12,2),
    preferred_locations TEXT, -- JSON array of cities/areas
    property_types TEXT, -- JSON array of preferred types
    min_bedrooms INTEGER,
    min_bathrooms DECIMAL(3,1),
    min_square_feet INTEGER,
    max_hoa_fees DECIMAL(8,2),
    must_have_features TEXT, -- JSON array of required features
    nice_to_have_features TEXT, -- JSON array of preferred features
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- New Table: Professional Service Providers (for transaction tracking)
CREATE TABLE IF NOT EXISTS service_providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_type VARCHAR(50), -- escrow, title, lender, inspector, appraiser
    company_name VARCHAR(100),
    contact_name VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    specializations TEXT,
    preferred_provider BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- New Table: Form Completion History
CREATE TABLE IF NOT EXISTS form_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER,
    form_type VARCHAR(100),
    form_name VARCHAR(200),
    completion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_by INTEGER, -- agent_id
    completion_method VARCHAR(50), -- auto, manual, hybrid
    completion_time_minutes INTEGER,
    client_signature_date DATE,
    notes TEXT,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (completed_by) REFERENCES agents(id)
);

-- New Table: Market Conditions Data (for Market Conditions Advisory)
CREATE TABLE IF NOT EXISTS market_conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area VARCHAR(100), -- city or region
    property_type VARCHAR(50),
    month_year VARCHAR(7), -- YYYY-MM format
    avg_days_on_market INTEGER,
    median_sale_price DECIMAL(12,2),
    price_per_sqft DECIMAL(8,2),
    inventory_levels INTEGER,
    market_trend VARCHAR(20), -- rising, stable, declining
    competitive_level VARCHAR(20), -- high, medium, low
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample service providers
INSERT OR IGNORE INTO service_providers (provider_type, company_name, contact_name, phone, email, preferred_provider) VALUES
('escrow', 'First American Title', 'John Smith', '(555) 123-4567', 'john@firstam.com', TRUE),
('title', 'Chicago Title Company', 'Mary Johnson', '(555) 234-5678', 'mary@chicagotitle.com', TRUE),
('lender', 'Wells Fargo Home Mortgage', 'Bob Wilson', '(555) 345-6789', 'bob@wellsfargo.com', TRUE),
('inspector', 'Professional Home Inspections', 'Lisa Davis', '(555) 456-7890', 'lisa@prohome.com', TRUE),
('appraiser', 'California Appraisal Services', 'Mike Chen', '(555) 567-8901', 'mike@calappraisal.com', TRUE);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email);
CREATE INDEX IF NOT EXISTS idx_properties_mls ON properties(mls_number);
CREATE INDEX IF NOT EXISTS idx_properties_apn ON properties(apn);
CREATE INDEX IF NOT EXISTS idx_transactions_client ON transactions(client_id);
CREATE INDEX IF NOT EXISTS idx_transactions_property ON transactions(property_id);
CREATE INDEX IF NOT EXISTS idx_transactions_closing_date ON transactions(closing_date);
CREATE INDEX IF NOT EXISTS idx_search_criteria_client ON property_search_criteria(client_id);
CREATE INDEX IF NOT EXISTS idx_form_completions_transaction ON form_completions(transaction_id);
CREATE INDEX IF NOT EXISTS idx_market_conditions_area ON market_conditions(area, property_type);

-- Create views for common form data queries
CREATE VIEW IF NOT EXISTS buyer_representation_data AS
SELECT 
    c.first_name,
    c.last_name,
    c.email,
    c.phone,
    c.mobile_phone,
    c.mailing_address_line1,
    c.mailing_city,
    c.mailing_state,
    c.mailing_zip_code,
    c.spouse_name,
    c.emergency_contact_name,
    c.emergency_contact_phone,
    c.pre_approval_amount,
    psc.min_price,
    psc.max_price,
    psc.preferred_locations,
    psc.property_types,
    a.first_name as agent_first_name,
    a.last_name as agent_last_name,
    a.license_number,
    a.brokerage,
    a.commission_split
FROM clients c
LEFT JOIN property_search_criteria psc ON c.id = psc.client_id
LEFT JOIN agents a ON a.id = 1; -- Default agent - should be parameterized

CREATE VIEW IF NOT EXISTS transaction_summary AS
SELECT 
    t.*,
    c.first_name as buyer_first_name,
    c.last_name as buyer_last_name,
    c.phone as buyer_phone,
    c.email as buyer_email,
    p.property_address,
    p.property_city,
    p.property_state,
    p.property_zip,
    p.mls_number,
    p.apn,
    p.property_type,
    a.first_name as agent_first_name,
    a.last_name as agent_last_name,
    a.license_number,
    a.brokerage
FROM transactions t
LEFT JOIN clients c ON t.client_id = c.id
LEFT JOIN properties p ON t.property_id = p.id
LEFT JOIN agents a ON a.id = 1; -- Default agent - should be parameterized

-- Validation constraints
-- Ensure email addresses are valid format
-- Ensure phone numbers are valid format  
-- Ensure dates are logical (closing date after contract date, etc.)

-- Sample data population queries (commented out - run as needed)
/*
-- Sample client with full information
INSERT INTO clients (
    first_name, last_name, email, phone, mobile_phone,
    mailing_address_line1, mailing_city, mailing_state, mailing_zip_code,
    spouse_name, spouse_email, spouse_phone,
    emergency_contact_name, emergency_contact_phone, emergency_contact_relationship,
    date_of_birth, employer, occupation, annual_income, credit_score,
    pre_approval_amount, pre_approval_date, pre_approval_lender,
    client_type, lead_source
) VALUES (
    'John', 'Doe', 'john.doe@email.com', '(555) 123-4567', '(555) 987-6543',
    '123 Main Street', 'Los Angeles', 'CA', '90210',
    'Jane Doe', 'jane.doe@email.com', '(555) 987-6544',
    'Bob Smith', '(555) 111-2222', 'Brother',
    '1985-06-15', 'Tech Corp', 'Software Engineer', 120000.00, 750,
    850000.00, '2025-01-15', 'Wells Fargo',
    'buyer', 'Website'
);

-- Sample property search criteria
INSERT INTO property_search_criteria (
    client_id, min_price, max_price, preferred_locations, property_types,
    min_bedrooms, min_bathrooms, min_square_feet, max_hoa_fees,
    must_have_features, nice_to_have_features
) VALUES (
    1, 700000.00, 850000.00, 
    '["Los Angeles", "Beverly Hills", "Santa Monica"]',
    '["Single Family Residence", "Townhouse"]',
    3, 2.0, 2000, 500.00,
    '["2-car garage", "Move-in ready"]',
    '["Pool", "Fireplace", "Updated kitchen"]'
);
*/