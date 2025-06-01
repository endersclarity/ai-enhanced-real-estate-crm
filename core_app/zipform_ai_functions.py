#!/usr/bin/env python3
"""
Enhanced AI-Callable Functions for ZipForm Integration
Complete CRM functions supporting all ZipForm Transaction Cover Sheet fields
"""

import sqlite3
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import json

DATABASE_PATH = 'real_estate_crm.db'

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# ENHANCED CLIENT MANAGEMENT FUNCTIONS
# ============================================================================

def create_client_zipform(first_name, last_name, **kwargs):
    """
    Create a new client with full ZipForm field support.
    
    Args:
        first_name (str): Client's first name (required)
        last_name (str): Client's last name (required)
        **kwargs: ZipForm fields including:
            - middle_initial, email, home_phone, business_phone, cellular_phone, fax_number
            - street_address, city, state, zip_code, county
            - client_type, employer, occupation, annual_income, ssn_last_four
            - preferred_contact_method, notes, auto_signature_enabled
    
    Returns:
        dict: {'success': bool, 'client_id': int, 'message': str, 'conflicts': list}
    """
    try:
        conn = get_db_connection()
        
        # Check for existing client conflicts
        conflicts = []
        if kwargs.get('email'):
            existing = conn.execute(
                'SELECT id, first_name, last_name FROM clients WHERE email = ?', 
                (kwargs['email'],)
            ).fetchone()
            if existing:
                conflicts.append(f"Email {kwargs['email']} already exists for {existing['first_name']} {existing['last_name']}")
        
        if conflicts:
            conn.close()
            return {
                'success': False,
                'client_id': None,
                'message': 'Conflicts detected - need user confirmation',
                'conflicts': conflicts
            }
        
        # Insert new client with all ZipForm fields
        cursor = conn.execute('''
            INSERT INTO clients (
                first_name, last_name, middle_initial, email, home_phone, business_phone,
                cellular_phone, fax_number, preferred_contact_method, street_address,
                city, state, zip_code, county, client_type, employer, occupation,
                annual_income, ssn_last_four, notes, auto_signature_enabled
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            first_name, last_name, kwargs.get('middle_initial'),
            kwargs.get('email'), kwargs.get('home_phone'), kwargs.get('business_phone'),
            kwargs.get('cellular_phone'), kwargs.get('fax_number'),
            kwargs.get('preferred_contact_method', 'email'), kwargs.get('street_address'),
            kwargs.get('city'), kwargs.get('state'), kwargs.get('zip_code'),
            kwargs.get('county'), kwargs.get('client_type', 'buyer'),
            kwargs.get('employer'), kwargs.get('occupation'), kwargs.get('annual_income'),
            kwargs.get('ssn_last_four'), kwargs.get('notes'),
            kwargs.get('auto_signature_enabled', False)
        ))
        
        client_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'client_id': client_id,
            'message': f'Successfully created client: {first_name} {last_name}',
            'conflicts': []
        }
        
    except Exception as e:
        return {
            'success': False,
            'client_id': None,
            'message': f'Error creating client: {str(e)}',
            'conflicts': []
        }

# ============================================================================
# ENHANCED PROPERTY MANAGEMENT FUNCTIONS  
# ============================================================================

def create_property_zipform(street_address, city, state, zip_code, **kwargs):
    """
    Create a new property with full ZipForm field support.
    
    Args:
        street_address (str): Property street address (required)
        city (str): City (required)
        state (str): State (required)
        zip_code (str): ZIP code (required)
        **kwargs: ZipForm fields including all property details, legal info, financial data
    
    Returns:
        dict: {'success': bool, 'property_id': int, 'message': str, 'conflicts': list}
    """
    try:
        conn = get_db_connection()
        
        # Check for existing property conflicts
        conflicts = []
        existing = conn.execute(
            'SELECT id FROM properties WHERE street_address = ? AND city = ? AND state = ?',
            (street_address, city, state)
        ).fetchone()
        
        if existing:
            conflicts.append(f"Property already exists at {street_address}, {city}, {state}")
        
        if conflicts:
            conn.close()
            return {
                'success': False,
                'property_id': None,
                'message': 'Property conflicts detected - need user confirmation',
                'conflicts': conflicts
            }
        
        # Insert new property with all ZipForm fields
        cursor = conn.execute('''
            INSERT INTO properties (
                street_address, city, state, zip_code, county, township, legal_description,
                tax_id, assessor_parcel_number, lot_number, unit_number, block, subdivision,
                plat_book, page_number, mls_number, listing_date, expiration_date,
                listed_price, original_price, property_type, year_built, bedrooms, bathrooms,
                square_feet, lot_size_acres, lot_size_sqft, mobile_home_year, mobile_home_make,
                mobile_home_serial_number, mobile_home_hcd_decal, balance_first_mortgage,
                balance_second_mortgage, other_liens, other_liens_description, total_encumbrances,
                homeowner_assoc_dues, transfer_fee, doc_prep_fees, property_includes,
                property_excludes, leased_items, supplemental_info, purchase_price,
                purchase_agreement_date, closing_date, deposit_amount, deposit_amount_1st_increase,
                deposit_amount_2nd_increase, deposit_amount_3rd_increase, offer_date,
                expire_date, expire_time, offer_acceptance_date, total_amount_financed,
                property_description, public_remarks, private_remarks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            street_address, city, state, zip_code, kwargs.get('county'), kwargs.get('township'),
            kwargs.get('legal_description'), kwargs.get('tax_id'), kwargs.get('assessor_parcel_number'),
            kwargs.get('lot_number'), kwargs.get('unit_number'), kwargs.get('block'),
            kwargs.get('subdivision'), kwargs.get('plat_book'), kwargs.get('page_number'),
            kwargs.get('mls_number'), kwargs.get('listing_date'), kwargs.get('expiration_date'),
            kwargs.get('listed_price'), kwargs.get('original_price'),
            kwargs.get('property_type', 'Residential'), kwargs.get('year_built'),
            kwargs.get('bedrooms'), kwargs.get('bathrooms'), kwargs.get('square_feet'),
            kwargs.get('lot_size_acres'), kwargs.get('lot_size_sqft'), kwargs.get('mobile_home_year'),
            kwargs.get('mobile_home_make'), kwargs.get('mobile_home_serial_number'),
            kwargs.get('mobile_home_hcd_decal'), kwargs.get('balance_first_mortgage'),
            kwargs.get('balance_second_mortgage'), kwargs.get('other_liens'),
            kwargs.get('other_liens_description'), kwargs.get('total_encumbrances'),
            kwargs.get('homeowner_assoc_dues'), kwargs.get('transfer_fee'), kwargs.get('doc_prep_fees'),
            kwargs.get('property_includes'), kwargs.get('property_excludes'), kwargs.get('leased_items'),
            kwargs.get('supplemental_info'), kwargs.get('purchase_price'),
            kwargs.get('purchase_agreement_date'), kwargs.get('closing_date'),
            kwargs.get('deposit_amount'), kwargs.get('deposit_amount_1st_increase'),
            kwargs.get('deposit_amount_2nd_increase'), kwargs.get('deposit_amount_3rd_increase'),
            kwargs.get('offer_date'), kwargs.get('expire_date'), kwargs.get('expire_time'),
            kwargs.get('offer_acceptance_date'), kwargs.get('total_amount_financed'),
            kwargs.get('property_description'), kwargs.get('public_remarks'), kwargs.get('private_remarks')
        ))
        
        property_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'property_id': property_id,
            'message': f'Successfully created property: {street_address}, {city}',
            'conflicts': []
        }
        
    except Exception as e:
        return {
            'success': False,
            'property_id': None,
            'message': f'Error creating property: {str(e)}',
            'conflicts': []
        }

# ============================================================================
# TRANSACTION MANAGEMENT FUNCTIONS
# ============================================================================

def create_transaction(transaction_type, property_id, buyer_client_id=None, seller_client_id=None, **kwargs):
    """
    Create a new transaction with full ZipForm support.
    
    Args:
        transaction_type (str): 'purchase', 'sale', 'lease'
        property_id (int): Property ID
        buyer_client_id (int): Buyer client ID (optional)
        seller_client_id (int): Seller client ID (optional)
        **kwargs: All ZipForm transaction fields
    
    Returns:
        dict: {'success': bool, 'transaction_id': int, 'message': str}
    """
    try:
        conn = get_db_connection()
        
        cursor = conn.execute('''
            INSERT INTO transactions (
                transaction_type, property_id, buyer_client_id, seller_client_id,
                purchase_price, original_offer_price, final_sale_price, offer_date,
                offer_expiration_date, offer_expiration_time, acceptance_date, contract_date,
                closing_date, down_payment_amount, down_payment_percentage, loan_amount,
                loan_term_years, interest_rate, total_amount_financed, earnest_money_amount,
                deposit_amount, deposit_1st_increase, deposit_2nd_increase, deposit_3rd_increase,
                listing_broker_id, selling_broker_id, listing_agent_id, selling_agent_id,
                lender_id, title_company_id, escrow_company_id, appraisal_company_id,
                pest_control_providers, disclosure_providers, home_warranty_providers,
                hoa_providers, transaction_coordinators, status, financing_contingency_date,
                inspection_contingency_date, appraisal_contingency_date, title_contingency_date,
                sale_of_property_contingency_date, homeowners_insurance_contingency_date,
                hoa_approval_contingency_date, as_is_sale, seller_financing, home_warranty,
                notes, private_remarks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction_type, property_id, buyer_client_id, seller_client_id,
            kwargs.get('purchase_price'), kwargs.get('original_offer_price'),
            kwargs.get('final_sale_price'), kwargs.get('offer_date'),
            kwargs.get('offer_expiration_date'), kwargs.get('offer_expiration_time'),
            kwargs.get('acceptance_date'), kwargs.get('contract_date'), kwargs.get('closing_date'),
            kwargs.get('down_payment_amount'), kwargs.get('down_payment_percentage'),
            kwargs.get('loan_amount'), kwargs.get('loan_term_years'), kwargs.get('interest_rate'),
            kwargs.get('total_amount_financed'), kwargs.get('earnest_money_amount'),
            kwargs.get('deposit_amount'), kwargs.get('deposit_1st_increase'),
            kwargs.get('deposit_2nd_increase'), kwargs.get('deposit_3rd_increase'),
            kwargs.get('listing_broker_id'), kwargs.get('selling_broker_id'),
            kwargs.get('listing_agent_id'), kwargs.get('selling_agent_id'),
            kwargs.get('lender_id'), kwargs.get('title_company_id'), kwargs.get('escrow_company_id'),
            kwargs.get('appraisal_company_id'), kwargs.get('pest_control_providers'),
            kwargs.get('disclosure_providers'), kwargs.get('home_warranty_providers'),
            kwargs.get('hoa_providers'), kwargs.get('transaction_coordinators'),
            kwargs.get('status', 'pending'), kwargs.get('financing_contingency_date'),
            kwargs.get('inspection_contingency_date'), kwargs.get('appraisal_contingency_date'),
            kwargs.get('title_contingency_date'), kwargs.get('sale_of_property_contingency_date'),
            kwargs.get('homeowners_insurance_contingency_date'), kwargs.get('hoa_approval_contingency_date'),
            kwargs.get('as_is_sale', False), kwargs.get('seller_financing', False),
            kwargs.get('home_warranty', False), kwargs.get('notes'), kwargs.get('private_remarks')
        ))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'transaction_id': transaction_id,
            'message': f'Successfully created {transaction_type} transaction',
        }
        
    except Exception as e:
        return {
            'success': False,
            'transaction_id': None,
            'message': f'Error creating transaction: {str(e)}'
        }

# ============================================================================
# BROKER/AGENT MANAGEMENT FUNCTIONS
# ============================================================================

def create_broker_agent(firm_name, agent_name, role, **kwargs):
    """
    Create a new broker/agent record.
    
    Args:
        firm_name (str): Brokerage firm name
        agent_name (str): Agent's name
        role (str): 'listing_office', 'selling_office', 'listing_agent', 'selling_agent'
        **kwargs: Additional broker/agent fields
    
    Returns:
        dict: {'success': bool, 'broker_agent_id': int, 'message': str}
    """
    try:
        conn = get_db_connection()
        
        cursor = conn.execute('''
            INSERT INTO brokers_agents (
                firm_name, firm_address, firm_city, firm_state, firm_zip_code,
                firm_phone, firm_dre_license, agent_name, agent_phone, agent_cellular,
                agent_fax, agent_email, agent_dre_license, role
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            firm_name, kwargs.get('firm_address'), kwargs.get('firm_city'),
            kwargs.get('firm_state'), kwargs.get('firm_zip_code'), kwargs.get('firm_phone'),
            kwargs.get('firm_dre_license'), agent_name, kwargs.get('agent_phone'),
            kwargs.get('agent_cellular'), kwargs.get('agent_fax'), kwargs.get('agent_email'),
            kwargs.get('agent_dre_license'), role
        ))
        
        broker_agent_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'broker_agent_id': broker_agent_id,
            'message': f'Successfully created {role}: {agent_name} at {firm_name}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'broker_agent_id': None,
            'message': f'Error creating broker/agent: {str(e)}'
        }

# ============================================================================
# SERVICE PROVIDER MANAGEMENT FUNCTIONS
# ============================================================================

def create_lender(company_name, **kwargs):
    """Create a new lender record"""
    try:
        conn = get_db_connection()
        
        cursor = conn.execute('''
            INSERT INTO lenders (
                company_name, street_address, city, state, zip_code, phone, fax,
                officer_name, officer_cell_phone, officer_email, mortgage_type, mortgage_type_other
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            company_name, kwargs.get('street_address'), kwargs.get('city'),
            kwargs.get('state'), kwargs.get('zip_code'), kwargs.get('phone'),
            kwargs.get('fax'), kwargs.get('officer_name'), kwargs.get('officer_cell_phone'),
            kwargs.get('officer_email'), kwargs.get('mortgage_type'), kwargs.get('mortgage_type_other')
        ))
        
        lender_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'lender_id': lender_id,
            'message': f'Successfully created lender: {company_name}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'lender_id': None,
            'message': f'Error creating lender: {str(e)}'
        }

def create_title_company(company_name, **kwargs):
    """Create a new title company record"""
    try:
        conn = get_db_connection()
        
        cursor = conn.execute('''
            INSERT INTO title_companies (
                company_name, street_address, city, state, zip_code, phone, fax,
                officer_name, officer_cell_phone, officer_email
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            company_name, kwargs.get('street_address'), kwargs.get('city'),
            kwargs.get('state'), kwargs.get('zip_code'), kwargs.get('phone'),
            kwargs.get('fax'), kwargs.get('officer_name'), kwargs.get('officer_cell_phone'),
            kwargs.get('officer_email')
        ))
        
        title_company_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'title_company_id': title_company_id,
            'message': f'Successfully created title company: {company_name}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'title_company_id': None,
            'message': f'Error creating title company: {str(e)}'
        }

def create_escrow_company(company_name, **kwargs):
    """Create a new escrow company record"""
    try:
        conn = get_db_connection()
        
        cursor = conn.execute('''
            INSERT INTO escrow_companies (
                company_name, street_address, city, state, zip_code, phone, fax,
                officer_name, officer_license_number, officer_email, escrow_number,
                closing_date, deposit_one, deposit_two
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            company_name, kwargs.get('street_address'), kwargs.get('city'),
            kwargs.get('state'), kwargs.get('zip_code'), kwargs.get('phone'),
            kwargs.get('fax'), kwargs.get('officer_name'), kwargs.get('officer_license_number'),
            kwargs.get('officer_email'), kwargs.get('escrow_number'), kwargs.get('closing_date'),
            kwargs.get('deposit_one'), kwargs.get('deposit_two')
        ))
        
        escrow_company_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'escrow_company_id': escrow_company_id,
            'message': f'Successfully created escrow company: {company_name}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'escrow_company_id': None,
            'message': f'Error creating escrow company: {str(e)}'
        }

def create_service_provider(company_name, service_type, **kwargs):
    """
    Create a service provider (pest control, disclosure, home warranty, etc.)
    
    Args:
        company_name (str): Company name
        service_type (str): 'pest_control', 'disclosure', 'home_warranty', 'hoa', 'transaction_coordinator'
        **kwargs: Additional service provider fields
    """
    try:
        conn = get_db_connection()
        
        cursor = conn.execute('''
            INSERT INTO service_providers (
                company_name, street_address, city, state, zip_code, phone, fax,
                representative_name, representative_cell_phone, representative_email,
                service_type, coordinator_side
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            company_name, kwargs.get('street_address'), kwargs.get('city'),
            kwargs.get('state'), kwargs.get('zip_code'), kwargs.get('phone'),
            kwargs.get('fax'), kwargs.get('representative_name'), kwargs.get('representative_cell_phone'),
            kwargs.get('representative_email'), service_type, kwargs.get('coordinator_side')
        ))
        
        service_provider_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'service_provider_id': service_provider_id,
            'message': f'Successfully created {service_type} provider: {company_name}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'service_provider_id': None,
            'message': f'Error creating service provider: {str(e)}'
        }

# ============================================================================
# ZIPFORM FUNCTION REGISTRY FOR AI DISCOVERY
# ============================================================================

ZIPFORM_AI_FUNCTIONS = {
    'create_client_zipform': {
        'function': create_client_zipform,
        'description': 'Create client with full ZipForm contact and address fields',
        'required_params': ['first_name', 'last_name'],
        'optional_params': ['middle_initial', 'email', 'home_phone', 'business_phone', 'cellular_phone', 'fax_number', 'street_address', 'city', 'state', 'zip_code', 'county', 'client_type', 'auto_signature_enabled'],
        'example': 'create_client_zipform("John", "Smith", email="john@email.com", home_phone="555-1234", business_phone="555-5678", auto_signature_enabled=True)'
    },
    'create_property_zipform': {
        'function': create_property_zipform,
        'description': 'Create property with complete ZipForm legal and financial details',
        'required_params': ['street_address', 'city', 'state', 'zip_code'],
        'optional_params': ['mls_number', 'legal_description', 'tax_id', 'assessor_parcel_number', 'listed_price', 'homeowner_assoc_dues', 'mobile_home_details'],
        'example': 'create_property_zipform("123 Main St", "Sacramento", "CA", "95814", mls_number="ML123456", listed_price=500000)'
    },
    'create_transaction': {
        'function': create_transaction,
        'description': 'Create complete transaction with all ZipForm offer and closing details',
        'required_params': ['transaction_type', 'property_id'],
        'optional_params': ['buyer_client_id', 'seller_client_id', 'purchase_price', 'offer_date', 'closing_date', 'earnest_money_amount', 'contingency_dates'],
        'example': 'create_transaction("purchase", 123, buyer_client_id=456, purchase_price=500000, offer_date="2024-01-15")'
    },
    'create_broker_agent': {
        'function': create_broker_agent,
        'description': 'Create broker/agent with firm details and DRE license information',
        'required_params': ['firm_name', 'agent_name', 'role'],
        'optional_params': ['firm_address', 'firm_dre_license', 'agent_phone', 'agent_email', 'agent_dre_license'],
        'example': 'create_broker_agent("Coldwell Banker", "Jane Agent", "listing_agent", agent_phone="555-9999")'
    },
    'create_lender': {
        'function': create_lender,
        'description': 'Create lender with loan officer and mortgage type information',
        'required_params': ['company_name'],
        'optional_params': ['officer_name', 'phone', 'mortgage_type', 'officer_email'],
        'example': 'create_lender("Wells Fargo", officer_name="John Banker", mortgage_type="Conv")'
    },
    'create_title_company': {
        'function': create_title_company,
        'description': 'Create title company with title officer information',
        'required_params': ['company_name'],
        'optional_params': ['officer_name', 'phone', 'officer_email'],
        'example': 'create_title_company("First American Title", officer_name="Mary Title")'
    },
    'create_escrow_company': {
        'function': create_escrow_company,
        'description': 'Create escrow company with escrow officer and closing details',
        'required_params': ['company_name'],
        'optional_params': ['officer_name', 'escrow_number', 'closing_date', 'deposit_dates'],
        'example': 'create_escrow_company("ABC Escrow", officer_name="Bob Escrow", escrow_number="E123456")'
    },
    'create_service_provider': {
        'function': create_service_provider,
        'description': 'Create service provider (pest control, home warranty, transaction coordinator, etc.)',
        'required_params': ['company_name', 'service_type'],
        'optional_params': ['representative_name', 'phone', 'coordinator_side'],
        'example': 'create_service_provider("ABC Pest Control", "pest_control", representative_name="Joe Exterminator")'
    }
}

if __name__ == "__main__":
    print("🏠 ZipForm AI Functions Ready")
    print("=" * 50)
    print("Available ZipForm functions:")
    for func_name, info in ZIPFORM_AI_FUNCTIONS.items():
        print(f"  {func_name}: {info['description']}")