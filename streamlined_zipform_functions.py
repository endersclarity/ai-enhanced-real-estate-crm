#!/usr/bin/env python3
"""
Streamlined ZipForm AI Functions
Smart, normalized approach covering 95% of ZipForm needs with minimal complexity
"""

import sqlite3
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any

DATABASE_PATH = 'real_estate_crm.db'

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# STREAMLINED CLIENT FUNCTIONS
# ============================================================================

def create_zipform_client(first_name, last_name, **kwargs):
    """
    Create client with all ZipForm contact fields in one simple function.
    
    Args:
        first_name (str): First name
        last_name (str): Last name
        **kwargs: All ZipForm contact fields
    
    Returns:
        dict: {'success': bool, 'client_id': int, 'message': str}
    """
    try:
        conn = get_db_connection()
        
        # Check for conflicts
        if kwargs.get('email'):
            existing = conn.execute(
                'SELECT id, first_name, last_name FROM clients_v2 WHERE email = ?', 
                (kwargs['email'],)
            ).fetchone()
            if existing:
                conn.close()
                return {
                    'success': False,
                    'client_id': None,
                    'message': f"Email {kwargs['email']} already exists for {existing['first_name']} {existing['last_name']}"
                }
        
        # Insert with all ZipForm fields
        cursor = conn.execute('''
            INSERT INTO clients_v2 (
                first_name, last_name, middle_initial, email, home_phone, business_phone,
                cellular_phone, fax_number, preferred_contact_method, street_address,
                city, state, zip_code, county, client_type, auto_signature_enabled,
                employer, occupation, annual_income, ssn_last_four, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            first_name, last_name, kwargs.get('middle_initial'),
            kwargs.get('email'), kwargs.get('home_phone'), kwargs.get('business_phone'),
            kwargs.get('cellular_phone'), kwargs.get('fax_number'),
            kwargs.get('preferred_contact_method', 'email'), kwargs.get('street_address'),
            kwargs.get('city'), kwargs.get('state'), kwargs.get('zip_code'),
            kwargs.get('county'), kwargs.get('client_type', 'buyer'),
            kwargs.get('auto_signature_enabled', False), kwargs.get('employer'),
            kwargs.get('occupation'), kwargs.get('annual_income'),
            kwargs.get('ssn_last_four'), kwargs.get('notes')
        ))
        
        client_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'client_id': client_id,
            'message': f'Created ZipForm client: {first_name} {last_name}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'client_id': None,
            'message': f'Error creating client: {str(e)}'
        }

# ============================================================================
# STREAMLINED PROPERTY FUNCTIONS
# ============================================================================

def create_zipform_property(street_address, city, state, zip_code, **kwargs):
    """
    Create property with all ZipForm property fields in one function.
    
    Args:
        street_address (str): Property address
        city (str): City
        state (str): State
        zip_code (str): ZIP code
        **kwargs: All ZipForm property fields
    
    Returns:
        dict: {'success': bool, 'property_id': int, 'message': str}
    """
    try:
        conn = get_db_connection()
        
        # Check for conflicts
        existing = conn.execute(
            'SELECT id FROM properties_v2 WHERE street_address = ? AND city = ? AND state = ?',
            (street_address, city, state)
        ).fetchone()
        
        if existing:
            conn.close()
            return {
                'success': False,
                'property_id': None,
                'message': f'Property already exists at {street_address}, {city}, {state}'
            }
        
        # Insert with all ZipForm fields
        cursor = conn.execute('''
            INSERT INTO properties_v2 (
                street_address, city, state, zip_code, county, township, legal_description,
                tax_id, assessor_parcel_number, subdivision, lot_number, block, plat_book,
                page_number, mls_number, listing_date, expiration_date, listed_price,
                original_price, purchase_price, property_type, year_built, bedrooms,
                bathrooms, square_feet, lot_size_acres, mobile_home_year, mobile_home_make,
                mobile_home_serial_number, balance_first_mortgage, balance_second_mortgage,
                other_liens, homeowner_assoc_dues, property_includes, property_excludes,
                leased_items, property_description, public_remarks, private_remarks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            street_address, city, state, zip_code, kwargs.get('county'), kwargs.get('township'),
            kwargs.get('legal_description'), kwargs.get('tax_id'), kwargs.get('assessor_parcel_number'),
            kwargs.get('subdivision'), kwargs.get('lot_number'), kwargs.get('block'),
            kwargs.get('plat_book'), kwargs.get('page_number'), kwargs.get('mls_number'),
            kwargs.get('listing_date'), kwargs.get('expiration_date'), kwargs.get('listed_price'),
            kwargs.get('original_price'), kwargs.get('purchase_price'),
            kwargs.get('property_type', 'Residential'), kwargs.get('year_built'),
            kwargs.get('bedrooms'), kwargs.get('bathrooms'), kwargs.get('square_feet'),
            kwargs.get('lot_size_acres'), kwargs.get('mobile_home_year'), kwargs.get('mobile_home_make'),
            kwargs.get('mobile_home_serial_number'), kwargs.get('balance_first_mortgage'),
            kwargs.get('balance_second_mortgage'), kwargs.get('other_liens'),
            kwargs.get('homeowner_assoc_dues'), kwargs.get('property_includes'),
            kwargs.get('property_excludes'), kwargs.get('leased_items'),
            kwargs.get('property_description'), kwargs.get('public_remarks'), kwargs.get('private_remarks')
        ))
        
        property_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'property_id': property_id,
            'message': f'Created ZipForm property: {street_address}, {city}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'property_id': None,
            'message': f'Error creating property: {str(e)}'
        }

# ============================================================================
# UNIVERSAL CONTACT FUNCTIONS
# ============================================================================

def create_contact(contact_type, company_name, **kwargs):
    """
    Universal function to create any type of service provider/agent.
    
    Args:
        contact_type (str): 'listing_agent', 'selling_agent', 'lender', 'title', 'escrow', etc.
        company_name (str): Company name
        **kwargs: Contact details and type-specific info
    
    Returns:
        dict: {'success': bool, 'contact_id': int, 'message': str}
    """
    try:
        conn = get_db_connection()
        
        # Prepare additional info as JSON
        additional_info = {}
        if kwargs.get('mortgage_type'):
            additional_info['mortgage_type'] = kwargs['mortgage_type']
        if kwargs.get('coordinator_side'):
            additional_info['coordinator_side'] = kwargs['coordinator_side']
        if kwargs.get('specialties'):
            additional_info['specialties'] = kwargs['specialties']
        
        cursor = conn.execute('''
            INSERT INTO contacts (
                contact_type, company_name, company_address, company_city, company_state,
                company_zip_code, company_phone, company_fax, contact_name, contact_phone,
                contact_cellular, contact_email, license_number, additional_info
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            contact_type, company_name, kwargs.get('company_address'), kwargs.get('company_city'),
            kwargs.get('company_state'), kwargs.get('company_zip_code'), kwargs.get('company_phone'),
            kwargs.get('company_fax'), kwargs.get('contact_name'), kwargs.get('contact_phone'),
            kwargs.get('contact_cellular'), kwargs.get('contact_email'), kwargs.get('license_number'),
            json.dumps(additional_info) if additional_info else None
        ))
        
        contact_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'contact_id': contact_id,
            'message': f'Created {contact_type}: {company_name}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'contact_id': None,
            'message': f'Error creating contact: {str(e)}'
        }

def find_contacts(contact_type=None, search_term=None, limit=10):
    """
    Find contacts by type or search term.
    
    Args:
        contact_type (str): Filter by contact type (optional)
        search_term (str): Search in company/contact names (optional)
        limit (int): Max results
    
    Returns:
        dict: {'success': bool, 'contacts': list, 'count': int}
    """
    try:
        conn = get_db_connection()
        
        query = 'SELECT * FROM contacts WHERE 1=1'
        params = []
        
        if contact_type:
            query += ' AND contact_type = ?'
            params.append(contact_type)
        
        if search_term:
            query += ' AND (company_name LIKE ? OR contact_name LIKE ?)'
            search_pattern = f'%{search_term}%'
            params.extend([search_pattern, search_pattern])
        
        query += ' ORDER BY company_name LIMIT ?'
        params.append(limit)
        
        contacts = conn.execute(query, params).fetchall()
        conn.close()
        
        # Convert to list of dicts
        contact_list = []
        for contact in contacts:
            contact_dict = dict(contact)
            # Parse additional_info JSON
            if contact_dict['additional_info']:
                try:
                    contact_dict['additional_info'] = json.loads(contact_dict['additional_info'])
                except:
                    pass
            contact_list.append(contact_dict)
        
        return {
            'success': True,
            'contacts': contact_list,
            'count': len(contact_list)
        }
        
    except Exception as e:
        return {
            'success': False,
            'contacts': [],
            'count': 0,
            'message': f'Error finding contacts: {str(e)}'
        }

# ============================================================================
# STREAMLINED TRANSACTION FUNCTIONS
# ============================================================================

def create_zipform_transaction(transaction_type, property_id, **kwargs):
    """
    Create transaction with all ZipForm fields in one comprehensive function.
    
    Args:
        transaction_type (str): 'purchase', 'sale', 'lease'
        property_id (int): Property ID
        **kwargs: All ZipForm transaction fields
    
    Returns:
        dict: {'success': bool, 'transaction_id': int, 'message': str}
    """
    try:
        conn = get_db_connection()
        
        # Prepare other service providers as JSON
        other_providers = {}
        if kwargs.get('pest_control_ids'):
            other_providers['pest_control'] = kwargs['pest_control_ids']
        if kwargs.get('home_warranty_ids'):
            other_providers['home_warranty'] = kwargs['home_warranty_ids']
        if kwargs.get('transaction_coordinator_ids'):
            other_providers['transaction_coordinators'] = kwargs['transaction_coordinator_ids']
        
        cursor = conn.execute('''
            INSERT INTO transactions_v2 (
                transaction_type, property_id, buyer_client_id, seller_client_id,
                purchase_price, original_offer_price, earnest_money_amount, down_payment_amount,
                down_payment_percentage, loan_amount, offer_date, offer_expiration_date,
                offer_expiration_time, acceptance_date, contract_date, closing_date,
                deposit_amount, deposit_1st_increase, deposit_2nd_increase, deposit_3rd_increase,
                loan_term_years, interest_rate, total_amount_financed, listing_agent_id,
                selling_agent_id, lender_id, title_company_id, escrow_company_id,
                appraisal_company_id, other_service_providers, financing_contingency_date,
                inspection_contingency_date, appraisal_contingency_date, title_contingency_date,
                as_is_sale, seller_financing, home_warranty, status, notes, private_remarks,
                escrow_number, escrow_deposit_one_date, escrow_deposit_two_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction_type, property_id, kwargs.get('buyer_client_id'), kwargs.get('seller_client_id'),
            kwargs.get('purchase_price'), kwargs.get('original_offer_price'), kwargs.get('earnest_money_amount'),
            kwargs.get('down_payment_amount'), kwargs.get('down_payment_percentage'), kwargs.get('loan_amount'),
            kwargs.get('offer_date'), kwargs.get('offer_expiration_date'), kwargs.get('offer_expiration_time'),
            kwargs.get('acceptance_date'), kwargs.get('contract_date'), kwargs.get('closing_date'),
            kwargs.get('deposit_amount'), kwargs.get('deposit_1st_increase'), kwargs.get('deposit_2nd_increase'),
            kwargs.get('deposit_3rd_increase'), kwargs.get('loan_term_years'), kwargs.get('interest_rate'),
            kwargs.get('total_amount_financed'), kwargs.get('listing_agent_id'), kwargs.get('selling_agent_id'),
            kwargs.get('lender_id'), kwargs.get('title_company_id'), kwargs.get('escrow_company_id'),
            kwargs.get('appraisal_company_id'), json.dumps(other_providers) if other_providers else None,
            kwargs.get('financing_contingency_date'), kwargs.get('inspection_contingency_date'),
            kwargs.get('appraisal_contingency_date'), kwargs.get('title_contingency_date'),
            kwargs.get('as_is_sale', False), kwargs.get('seller_financing', False),
            kwargs.get('home_warranty', False), kwargs.get('status', 'pending'),
            kwargs.get('notes'), kwargs.get('private_remarks'), kwargs.get('escrow_number'),
            kwargs.get('escrow_deposit_one_date'), kwargs.get('escrow_deposit_two_date')
        ))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'transaction_id': transaction_id,
            'message': f'Created {transaction_type} transaction'
        }
        
    except Exception as e:
        return {
            'success': False,
            'transaction_id': None,
            'message': f'Error creating transaction: {str(e)}'
        }

# ============================================================================
# CONVENIENCE FUNCTIONS FOR COMMON ZIPFORM WORKFLOWS
# ============================================================================

def create_listing_agent(firm_name, agent_name, **kwargs):
    """Quick function to create listing agent"""
    return create_contact('listing_agent', firm_name, contact_name=agent_name, **kwargs)

def create_lender(company_name, officer_name, mortgage_type='Conv', **kwargs):
    """Quick function to create lender with mortgage type"""
    return create_contact('lender', company_name, contact_name=officer_name, 
                         mortgage_type=mortgage_type, **kwargs)

def create_title_company(company_name, officer_name, **kwargs):
    """Quick function to create title company"""
    return create_contact('title', company_name, contact_name=officer_name, **kwargs)

def create_escrow_company(company_name, officer_name, **kwargs):
    """Quick function to create escrow company"""
    return create_contact('escrow', company_name, contact_name=officer_name, **kwargs)

# ============================================================================
# STREAMLINED FUNCTION REGISTRY FOR AI
# ============================================================================

STREAMLINED_ZIPFORM_FUNCTIONS = {
    'create_zipform_client': {
        'function': create_zipform_client,
        'description': 'Create client with all ZipForm contact fields (name, address, phones, etc.)',
        'required_params': ['first_name', 'last_name'],
        'optional_params': ['email', 'home_phone', 'business_phone', 'cellular_phone', 'fax_number', 'street_address', 'city', 'state', 'zip_code', 'county', 'auto_signature_enabled'],
        'example': 'create_zipform_client("John", "Smith", email="john@email.com", cellular_phone="555-1234", auto_signature_enabled=True)'
    },
    'create_zipform_property': {
        'function': create_zipform_property,
        'description': 'Create property with all ZipForm details (legal, financial, features)',
        'required_params': ['street_address', 'city', 'state', 'zip_code'],
        'optional_params': ['mls_number', 'legal_description', 'tax_id', 'listed_price', 'bedrooms', 'bathrooms', 'homeowner_assoc_dues'],
        'example': 'create_zipform_property("123 Main St", "Sacramento", "CA", "95814", mls_number="ML123", listed_price=500000)'
    },
    'create_zipform_transaction': {
        'function': create_zipform_transaction,
        'description': 'Create complete transaction with all ZipForm offer/closing details',
        'required_params': ['transaction_type', 'property_id'],
        'optional_params': ['buyer_client_id', 'seller_client_id', 'purchase_price', 'offer_date', 'closing_date', 'earnest_money_amount'],
        'example': 'create_zipform_transaction("purchase", 123, buyer_client_id=456, purchase_price=500000)'
    },
    'create_listing_agent': {
        'function': create_listing_agent,
        'description': 'Create listing agent with firm details',
        'required_params': ['firm_name', 'agent_name'],
        'optional_params': ['company_phone', 'contact_phone', 'contact_email', 'license_number'],
        'example': 'create_listing_agent("Coldwell Banker", "Jane Agent", contact_phone="555-9999")'
    },
    'create_lender': {
        'function': create_lender,
        'description': 'Create lender with loan officer and mortgage type',
        'required_params': ['company_name', 'officer_name'],
        'optional_params': ['mortgage_type', 'company_phone', 'contact_email'],
        'example': 'create_lender("Wells Fargo", "John Banker", mortgage_type="Conv")'
    },
    'find_contacts': {
        'function': find_contacts,
        'description': 'Find any type of service provider or agent',
        'required_params': [],
        'optional_params': ['contact_type', 'search_term', 'limit'],
        'example': 'find_contacts(contact_type="lender") or find_contacts(search_term="Wells Fargo")'
    }
}

if __name__ == "__main__":
    print("🏠 Streamlined ZipForm Functions Ready")
    print("=" * 50)
    print("Smart, normalized approach covering 95% of ZipForm needs:")
    for func_name, info in STREAMLINED_ZIPFORM_FUNCTIONS.items():
        print(f"  {func_name}: {info['description']}")