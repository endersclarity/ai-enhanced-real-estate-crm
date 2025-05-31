-- Real Estate CRM Database Schema
-- Comprehensive data model for Narissa Realty client and transaction management

-- Client/Contact Management
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_type VARCHAR(20) NOT NULL CHECK (client_type IN ('buyer', 'seller', 'both')),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    middle_initial VARCHAR(5),
    email VARCHAR(255),
    phone_primary VARCHAR(20),
    phone_secondary VARCHAR(20),
    address_street VARCHAR(255),
    address_city VARCHAR(100),
    address_state VARCHAR(50),
    address_zip VARCHAR(20),
    employer VARCHAR(200),
    occupation VARCHAR(200),
    annual_income DECIMAL(12,2),
    ssn_last_four VARCHAR(4),
    preferred_contact_method VARCHAR(20) DEFAULT 'email',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Properties
CREATE TABLE properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address_street VARCHAR(255) NOT NULL,
    address_city VARCHAR(100) NOT NULL,
    address_state VARCHAR(50) NOT NULL,
    address_zip VARCHAR(20) NOT NULL,
    address_county VARCHAR(100),
    apn VARCHAR(50), -- Assessor's Parcel Number
    lot_number VARCHAR(50),
    block_number VARCHAR(50),
    subdivision_name VARCHAR(200),
    lot_size_sqft INTEGER,
    lot_size_acres DECIMAL(8,3),
    house_sqft INTEGER,
    bedrooms INTEGER,
    bathrooms DECIMAL(3,1),
    half_baths INTEGER,
    garage_spaces INTEGER,
    parking_spaces INTEGER,
    year_built INTEGER,
    property_type VARCHAR(50),
    zoning VARCHAR(20),
    hoa_name VARCHAR(200),
    hoa_dues DECIMAL(10,2),
    hoa_frequency VARCHAR(20), -- monthly, quarterly, annually
    property_description TEXT,
    listing_price DECIMAL(12,2),
    status VARCHAR(20) DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions/Offers
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    buyer_client_id INTEGER,
    seller_client_id INTEGER,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('purchase', 'sale', 'lease')),
    status VARCHAR(30) DEFAULT 'pending',
    
    -- Financial Details
    purchase_price DECIMAL(12,2),
    earnest_money_amount DECIMAL(10,2),
    down_payment_amount DECIMAL(12,2),
    down_payment_percentage DECIMAL(5,2),
    loan_amount DECIMAL(12,2),
    loan_term_years INTEGER,
    monthly_payment DECIMAL(10,2),
    interest_rate DECIMAL(5,3),
    property_taxes_annual DECIMAL(10,2),
    insurance_annual DECIMAL(10,2),
    hoa_dues_monthly DECIMAL(8,2),
    closing_costs DECIMAL(10,2),
    total_buyer_costs DECIMAL(12,2),
    
    -- Important Dates
    offer_date DATE,
    acceptance_date DATE,
    contract_date DATE,
    close_of_escrow_date DATE,
    possession_date DATE,
    
    -- Contingency Deadlines
    inspection_deadline DATE,
    appraisal_deadline DATE,
    loan_approval_deadline DATE,
    contingency_removal_date DATE,
    title_report_deadline DATE,
    
    -- Contingencies (Boolean flags)
    financing_contingency BOOLEAN DEFAULT FALSE,
    inspection_contingency BOOLEAN DEFAULT FALSE,
    appraisal_contingency BOOLEAN DEFAULT FALSE,
    title_contingency BOOLEAN DEFAULT FALSE,
    sale_of_property_contingency BOOLEAN DEFAULT FALSE,
    homeowners_insurance_contingency BOOLEAN DEFAULT FALSE,
    hoa_approval_contingency BOOLEAN DEFAULT FALSE,
    as_is_sale BOOLEAN DEFAULT FALSE,
    seller_financing BOOLEAN DEFAULT FALSE,
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (property_id) REFERENCES properties(id),
    FOREIGN KEY (buyer_client_id) REFERENCES clients(id),
    FOREIGN KEY (seller_client_id) REFERENCES clients(id)
);

-- Agents and Brokerages
CREATE TABLE agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_type VARCHAR(20) NOT NULL CHECK (agent_type IN ('buyer_agent', 'listing_agent', 'dual_agent')),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    license_number VARCHAR(50),
    dre_number VARCHAR(50), -- California DRE number
    brokerage_name VARCHAR(200),
    brokerage_address VARCHAR(255),
    brokerage_phone VARCHAR(20),
    is_primary_agent BOOLEAN DEFAULT FALSE, -- Is this Narissa?
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transaction Agents (Many-to-many relationship)
CREATE TABLE transaction_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    agent_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('buyer_agent', 'listing_agent', 'cooperating_agent')),
    commission_percentage DECIMAL(5,3),
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- Professional Services (Title, Escrow, Inspections, etc.)
CREATE TABLE service_providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_type VARCHAR(50) NOT NULL, -- title, escrow, inspection, attorney, etc.
    company_name VARCHAR(200) NOT NULL,
    contact_name VARCHAR(200),
    phone VARCHAR(20),
    email VARCHAR(255),
    address VARCHAR(255),
    specialization VARCHAR(100), -- general, termite, roof, hvac, etc.
    preferred_vendor BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transaction Services (Track which services are used for each transaction)
CREATE TABLE transaction_services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    service_provider_id INTEGER NOT NULL,
    service_date DATE,
    cost DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'scheduled',
    report_received BOOLEAN DEFAULT FALSE,
    notes TEXT,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (service_provider_id) REFERENCES service_providers(id)
);

-- Documents and Disclosures
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    document_type VARCHAR(100) NOT NULL, -- RPA, disclosure, inspection_report, etc.
    document_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    docusign_envelope_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'draft', -- draft, sent, signed, completed
    date_sent DATE,
    date_signed DATE,
    signers_required TEXT, -- JSON array of required signers
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);

-- Communication Log
CREATE TABLE communications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER,
    client_id INTEGER,
    communication_type VARCHAR(20) NOT NULL, -- email, text, call, meeting
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    subject VARCHAR(255),
    content TEXT,
    communication_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- Form Templates (Track available forms and their field mappings)
CREATE TABLE form_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_name VARCHAR(200) NOT NULL,
    form_type VARCHAR(100) NOT NULL, -- RPA, disclosure, addendum, etc.
    file_path VARCHAR(500),
    field_mapping TEXT, -- JSON mapping of form fields to database columns
    version VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generated Forms (Track forms generated from CRM data)
CREATE TABLE generated_forms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    form_template_id INTEGER NOT NULL,
    generated_file_path VARCHAR(500),
    generation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_snapshot TEXT, -- JSON snapshot of data used to generate form
    status VARCHAR(20) DEFAULT 'generated',
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (form_template_id) REFERENCES form_templates(id)
);

-- Indexes for better performance
CREATE INDEX idx_clients_email ON clients(email);
CREATE INDEX idx_clients_name ON clients(last_name, first_name);
CREATE INDEX idx_properties_address ON properties(address_city, address_state);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_dates ON transactions(offer_date, close_of_escrow_date);
CREATE INDEX idx_communications_date ON communications(communication_date);
CREATE INDEX idx_documents_transaction ON documents(transaction_id);