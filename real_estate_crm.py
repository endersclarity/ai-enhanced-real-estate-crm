#!/usr/bin/env python3
"""
Real Estate CRM Application
Comprehensive client and transaction management for Narissa Realty
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sqlite3
import json
from datetime import datetime, date
from decimal import Decimal
import os
import google.generativeai as genai
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change in production

DATABASE_PATH = 'real_estate_crm.db'

# Gemini API Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'your-gemini-api-key-here')

# Configure Gemini API
def configure_gemini():
    """Configure Gemini AI with API key"""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    except Exception as e:
        print(f"[GEMINI CONFIG ERROR] {str(e)}")
        return False

# Initialize Gemini configuration
GEMINI_CONFIGURED = configure_gemini()

def get_gemini_response(message, context="real estate CRM assistant"):
    """
    Get AI response from Gemini API using LangChain approach (same as working Langchain8n project)
    
    Args:
        message (str): User message
        context (str): Context for the AI assistant
    
    Returns:
        str: AI response or error message
    """
    if not GEMINI_CONFIGURED:
        return "AI service is currently unavailable. Please check configuration."
    
    try:
        # Use LangChain approach (like Langchain8n project)
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage, SystemMessage
        
        llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash-preview-04-17",
            google_api_key=GEMINI_API_KEY,
            temperature=0.1
        )
        
        # Create context-aware system message
        system_prompt = f"""You are a helpful {context} for Narissa Realty. 
        You assist real estate professionals with:
        - Client management and communication
        - Property information and analysis
        - Transaction guidance and workflow
        - Email processing and data extraction
        - Professional real estate advice
        
        Be professional, helpful, and knowledgeable about real estate processes.
        Keep responses concise but informative."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=message)
        ]
        
        # Generate response
        response = llm.invoke(messages)
        return response.content
        
    except Exception as e:
        print(f"[GEMINI API ERROR] {str(e)}")
        return f"I apologize, but I'm experiencing technical difficulties. Please try again later. (Error: {str(e)[:50]}...)"

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def init_database():
    """Initialize the database with schema"""
    if not os.path.exists(DATABASE_PATH):
        with open('real_estate_crm_schema.sql', 'r') as f:
            schema = f.read()
        
        conn = sqlite3.connect(DATABASE_PATH)
        conn.executescript(schema)
        conn.close()
        print("Database initialized successfully")

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# AI-CALLABLE DATABASE FUNCTIONS
# ============================================================================

def create_client(first_name, last_name, email=None, phone=None, client_type='buyer', **kwargs):
    """
    Create a new client in the CRM database.
    
    Args:
        first_name (str): Client's first name (required)
        last_name (str): Client's last name (required)
        email (str): Email address (optional but recommended)
        phone (str): Primary phone number (optional)
        client_type (str): 'buyer', 'seller', or 'both' (default: 'buyer')
        **kwargs: Additional client fields (address, occupation, income, etc.)
    
    Returns:
        dict: {'success': bool, 'client_id': int, 'message': str, 'conflicts': list}
    """
    try:
        conn = get_db_connection()
        
        # Check for existing client with same name and email
        conflicts = []
        if email:
            existing = conn.execute(
                'SELECT id, first_name, last_name FROM clients WHERE email = ?', 
                (email,)
            ).fetchone()
            if existing:
                conflicts.append(f"Email {email} already exists for {existing['first_name']} {existing['last_name']}")
        
        # If conflicts exist, return them for user decision
        if conflicts:
            conn.close()
            return {
                'success': False,
                'client_id': None,
                'message': 'Conflicts detected - need user confirmation',
                'conflicts': conflicts
            }
        
        # Insert new client
        cursor = conn.execute('''
            INSERT INTO clients (
                first_name, last_name, email, phone_primary, client_type,
                phone_secondary, address_street, address_city, 
                address_state, address_zip, employer, occupation, annual_income,
                ssn_last_four, preferred_contact_method, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            first_name, last_name, email, phone, client_type,
            kwargs.get('phone_secondary'), kwargs.get('address_street'), 
            kwargs.get('address_city'), kwargs.get('address_state'), kwargs.get('address_zip'),
            kwargs.get('employer'), kwargs.get('occupation'),
            kwargs.get('annual_income'), kwargs.get('ssn_last_four'),
            kwargs.get('preferred_contact_method', 'email'), kwargs.get('notes')
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

def find_clients(search_term=None, client_type=None, limit=10):
    """
    Find clients matching search criteria.
    
    Args:
        search_term (str): Search in name, email, or phone (optional)
        client_type (str): Filter by client type: 'buyer', 'seller', 'both' (optional)
        limit (int): Maximum number of results (default: 10)
    
    Returns:
        dict: {'success': bool, 'clients': list, 'count': int, 'message': str}
    """
    try:
        conn = get_db_connection()
        
        query = '''
            SELECT id, first_name, last_name, email, phone_primary, client_type,
                   address_city, address_state, created_at
            FROM clients
            WHERE 1=1
        '''
        params = []
        
        if search_term:
            query += ''' AND (
                first_name LIKE ? OR last_name LIKE ? OR 
                email LIKE ? OR phone_primary LIKE ?
            )'''
            search_pattern = f'%{search_term}%'
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
        
        if client_type:
            query += ' AND client_type = ?'
            params.append(client_type)
        
        query += ' ORDER BY last_name, first_name LIMIT ?'
        params.append(limit)
        
        clients = conn.execute(query, params).fetchall()
        conn.close()
        
        # Convert to list of dicts for easier AI processing
        client_list = []
        for client in clients:
            client_list.append({
                'id': client['id'],
                'name': f"{client['first_name']} {client['last_name']}",
                'email': client['email'],
                'phone': client['phone_primary'],
                'type': client['client_type'],
                'location': f"{client['address_city']}, {client['address_state']}" if client['address_city'] else None,
                'created': client['created_at']
            })
        
        return {
            'success': True,
            'clients': client_list,
            'count': len(client_list),
            'message': f'Found {len(client_list)} clients'
        }
        
    except Exception as e:
        return {
            'success': False,
            'clients': [],
            'count': 0,
            'message': f'Error searching clients: {str(e)}'
        }

def update_client(client_id, **kwargs):
    """
    Update an existing client's information.
    
    Args:
        client_id (int): Client ID to update
        **kwargs: Fields to update (first_name, last_name, email, phone, etc.)
    
    Returns:
        dict: {'success': bool, 'message': str, 'updated_fields': list}
    """
    try:
        conn = get_db_connection()
        
        # Check if client exists
        existing = conn.execute('SELECT id, first_name, last_name FROM clients WHERE id = ?', (client_id,)).fetchone()
        if not existing:
            conn.close()
            return {
                'success': False,
                'message': f'Client with ID {client_id} not found',
                'updated_fields': []
            }
        
        # Build update query for provided fields
        valid_fields = [
            'first_name', 'last_name', 'email', 'phone_primary', 
            'phone_secondary', 'client_type', 'address_street', 'address_city',
            'address_state', 'address_zip', 'employer', 'occupation', 'annual_income',
            'ssn_last_four', 'preferred_contact_method', 'notes'
        ]
        
        update_fields = []
        params = []
        for field, value in kwargs.items():
            if field in valid_fields and value is not None:
                update_fields.append(f'{field} = ?')
                params.append(value)
        
        if not update_fields:
            conn.close()
            return {
                'success': False,
                'message': 'No valid fields provided for update',
                'updated_fields': []
            }
        
        # Execute update
        query = f"UPDATE clients SET {', '.join(update_fields)} WHERE id = ?"
        params.append(client_id)
        
        conn.execute(query, params)
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': f'Successfully updated client: {existing["first_name"]} {existing["last_name"]}',
            'updated_fields': list(kwargs.keys())
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error updating client: {str(e)}',
            'updated_fields': []
        }

def create_property(address_line1, city, state, zip_code, **kwargs):
    """
    Create a new property listing in the CRM database.
    
    Args:
        address_line1 (str): Street address (required)
        city (str): City (required)
        state (str): State (required)
        zip_code (str): ZIP code (required)
        **kwargs: Additional property fields (price, bedrooms, bathrooms, etc.)
    
    Returns:
        dict: {'success': bool, 'property_id': int, 'message': str, 'conflicts': list}
    """
    try:
        conn = get_db_connection()
        
        # Check for existing property at same address
        conflicts = []
        existing = conn.execute(
            'SELECT id FROM properties WHERE address_line1 = ? AND city = ? AND state = ?',
            (address_line1, city, state)
        ).fetchone()
        
        if existing:
            conflicts.append(f"Property already exists at {address_line1}, {city}, {state}")
        
        if conflicts:
            conn.close()
            return {
                'success': False,
                'property_id': None,
                'message': 'Property conflicts detected - need user confirmation',
                'conflicts': conflicts
            }
        
        # Insert new property - using actual schema field names
        cursor = conn.execute('''
            INSERT INTO properties (
                address_line1, address_line2, city, state, zip_code, mls_number,
                property_type, listing_type, bedrooms, bathrooms, square_feet, 
                lot_size, year_built, listing_price, property_description,
                public_remarks, private_remarks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            address_line1, kwargs.get('address_line2'), city, state, zip_code,
            kwargs.get('mls_number'), kwargs.get('property_type', 'single_family'),
            kwargs.get('listing_type', 'sale'), kwargs.get('bedrooms'), kwargs.get('bathrooms'),
            kwargs.get('square_feet'), kwargs.get('lot_size'), kwargs.get('year_built'),
            kwargs.get('listing_price'), kwargs.get('description'), kwargs.get('public_remarks'),
            kwargs.get('private_remarks')
        ))
        
        property_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'property_id': property_id,
            'message': f'Successfully created property: {address_line1}, {city}',
            'conflicts': []
        }
        
    except Exception as e:
        return {
            'success': False,
            'property_id': None,
            'message': f'Error creating property: {str(e)}',
            'conflicts': []
        }

def find_properties(search_term=None, min_price=None, max_price=None, bedrooms=None, city=None, limit=10):
    """
    Find properties matching search criteria.
    
    Args:
        search_term (str): Search in address or MLS number (optional)
        min_price (float): Minimum listing price (optional)
        max_price (float): Maximum listing price (optional)
        bedrooms (int): Number of bedrooms (optional)
        city (str): City filter (optional)
        limit (int): Maximum results (default: 10)
    
    Returns:
        dict: {'success': bool, 'properties': list, 'count': int, 'message': str}
    """
    try:
        conn = get_db_connection()
        
        query = '''
            SELECT id, address_line1, address_line2, city, state, zip_code,
                   property_type, bedrooms, bathrooms, square_feet, listing_price,
                   mls_number, listing_type, created_at
            FROM properties
            WHERE 1=1
        '''
        params = []
        
        if search_term:
            query += ''' AND (
                address_line1 LIKE ? OR city LIKE ? OR mls_number LIKE ?
            )'''
            search_pattern = f'%{search_term}%'
            params.extend([search_pattern, search_pattern, search_pattern])
        
        if min_price:
            query += ' AND listing_price >= ?'
            params.append(min_price)
        
        if max_price:
            query += ' AND listing_price <= ?'
            params.append(max_price)
        
        if bedrooms:
            query += ' AND bedrooms = ?'
            params.append(bedrooms)
        
        if city:
            query += ' AND city LIKE ?'
            params.append(f'%{city}%')
        
        query += ' ORDER BY listing_price DESC LIMIT ?'
        params.append(limit)
        
        properties = conn.execute(query, params).fetchall()
        conn.close()
        
        # Convert to list of dicts for AI processing
        property_list = []
        for prop in properties:
            address_parts = [prop['address_line1']]
            if prop['address_line2']:
                address_parts.append(prop['address_line2'])
            address_parts.extend([prop['city'], prop['state'], prop['zip_code']])
            
            property_list.append({
                'id': prop['id'],
                'address': ', '.join(filter(None, address_parts)),
                'type': prop['property_type'],
                'bedrooms': prop['bedrooms'],
                'bathrooms': prop['bathrooms'],
                'square_feet': prop['square_feet'],
                'price': prop['listing_price'],
                'mls': prop['mls_number'],
                'listing_type': prop['listing_type'],
                'created': prop['created_at']
            })
        
        return {
            'success': True,
            'properties': property_list,
            'count': len(property_list),
            'message': f'Found {len(property_list)} properties'
        }
        
    except Exception as e:
        return {
            'success': False,
            'properties': [],
            'count': 0,
            'message': f'Error searching properties: {str(e)}'
        }

# Function registry for AI discovery
AI_CALLABLE_FUNCTIONS = {
    'create_client': {
        'function': create_client,
        'description': 'Create a new client with contact information',
        'required_params': ['first_name', 'last_name'],
        'optional_params': ['email', 'phone', 'client_type', 'address_street', 'address_city', 'address_state', 'occupation'],
        'example': 'create_client("John", "Smith", email="john@email.com", phone="555-1234", client_type="buyer")'
    },
    'find_clients': {
        'function': find_clients,
        'description': 'Search for existing clients by name, email, or phone',
        'required_params': [],
        'optional_params': ['search_term', 'client_type', 'limit'],
        'example': 'find_clients("John Smith") or find_clients(client_type="buyer")'
    },
    'update_client': {
        'function': update_client,
        'description': 'Update existing client information',
        'required_params': ['client_id'],
        'optional_params': ['first_name', 'last_name', 'email', 'phone_primary', 'address_street'],
        'example': 'update_client(123, email="newemail@example.com", phone_primary="555-9999")'
    },
    'create_property': {
        'function': create_property,
        'description': 'Add a new property listing to the system',
        'required_params': ['address_line1', 'city', 'state', 'zip_code'],
        'optional_params': ['listing_price', 'bedrooms', 'bathrooms', 'square_feet', 'property_type', 'mls_number'],
        'example': 'create_property("123 Main St", "Sacramento", "CA", "95814", listing_price=500000, bedrooms=3)'
    },
    'find_properties': {
        'function': find_properties,
        'description': 'Search for properties by address, price range, or features',
        'required_params': [],
        'optional_params': ['search_term', 'min_price', 'max_price', 'bedrooms', 'city', 'limit'],
        'example': 'find_properties(city="Sacramento", min_price=400000, max_price=600000, bedrooms=3)'
    }
}

@app.route('/')
def dashboard():
    """Main dashboard view"""
    conn = get_db_connection()
    
    # Get dashboard statistics
    stats = {
        'total_clients': conn.execute('SELECT COUNT(*) as count FROM clients').fetchone()['count'],
        'active_transactions': conn.execute('SELECT COUNT(*) as count FROM transactions WHERE status IN ("pending", "in_progress", "under_contract")').fetchone()['count'],
        'properties': conn.execute('SELECT COUNT(*) as count FROM properties').fetchone()['count'],
        'this_month_closings': conn.execute('SELECT COUNT(*) as count FROM transactions WHERE close_of_escrow_date >= date("now", "start of month")').fetchone()['count']
    }
    
    # Get recent transactions
    recent_transactions = conn.execute('''
        SELECT t.id, t.status, t.purchase_price, t.offer_date, t.close_of_escrow_date,
               p.address_street, p.address_city,
               bc.first_name as buyer_first, bc.last_name as buyer_last,
               sc.first_name as seller_first, sc.last_name as seller_last
        FROM transactions t
        JOIN properties p ON t.property_id = p.id
        LEFT JOIN clients bc ON t.buyer_client_id = bc.id
        LEFT JOIN clients sc ON t.seller_client_id = sc.id
        ORDER BY t.created_at DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    return render_template('crm_dashboard.html', stats=stats, recent_transactions=recent_transactions)

@app.route('/clients')
def clients_list():
    """View all clients"""
    conn = get_db_connection()
    clients = conn.execute('''
        SELECT id, client_type, first_name, last_name, email, phone_primary, 
               address_city, address_state, created_at
        FROM clients 
        ORDER BY last_name, first_name
    ''').fetchall()
    conn.close()
    return render_template('clients_list.html', clients=clients)

@app.route('/clients/new', methods=['GET', 'POST'])
def new_client():
    """Add new client"""
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO clients (
                client_type, first_name, last_name, middle_initial, email, phone_primary,
                phone_secondary, address_street, address_city, address_state, address_zip,
                employer, occupation, annual_income, ssn_last_four, preferred_contact_method, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['client_type'], data['first_name'], data['last_name'], data.get('middle_initial'),
            data.get('email'), data.get('phone_primary'), data.get('phone_secondary'),
            data.get('address_street'), data.get('address_city'), data.get('address_state'),
            data.get('address_zip'), data.get('employer'), data.get('occupation'),
            data.get('annual_income') or None, data.get('ssn_last_four'),
            data.get('preferred_contact_method', 'email'), data.get('notes')
        ))
        conn.commit()
        conn.close()
        flash('Client added successfully!')
        return redirect(url_for('clients_list'))
    
    return render_template('client_form.html')

@app.route('/clients/<int:client_id>')
def client_detail(client_id):
    """View client details"""
    conn = get_db_connection()
    client = conn.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
    
    if not client:
        flash('Client not found!')
        return redirect(url_for('clients_list'))
    
    # Get client's transactions
    transactions = conn.execute('''
        SELECT t.*, p.address_street, p.address_city, p.address_state
        FROM transactions t
        JOIN properties p ON t.property_id = p.id
        WHERE t.buyer_client_id = ? OR t.seller_client_id = ?
        ORDER BY t.created_at DESC
    ''', (client_id, client_id)).fetchall()
    
    conn.close()
    return render_template('client_detail.html', client=client, transactions=transactions)

@app.route('/properties')
def properties_list():
    """View all properties"""
    conn = get_db_connection()
    properties = conn.execute('''
        SELECT id, address_street, address_city, address_state, address_zip,
               bedrooms, bathrooms, house_sqft, listing_price, status, created_at
        FROM properties 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('properties_list.html', properties=properties)

@app.route('/properties/new', methods=['GET', 'POST'])
def new_property():
    """Add new property"""
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO properties (
                address_street, address_city, address_state, address_zip, address_county,
                apn, lot_number, block_number, subdivision_name, lot_size_sqft, lot_size_acres,
                house_sqft, bedrooms, bathrooms, half_baths, garage_spaces, parking_spaces,
                year_built, property_type, zoning, hoa_name, hoa_dues, hoa_frequency,
                property_description, listing_price, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['address_street'], data['address_city'], data['address_state'], data['address_zip'],
            data.get('address_county'), data.get('apn'), data.get('lot_number'), data.get('block_number'),
            data.get('subdivision_name'), data.get('lot_size_sqft') or None, data.get('lot_size_acres') or None,
            data.get('house_sqft') or None, data.get('bedrooms') or None, data.get('bathrooms') or None,
            data.get('half_baths') or None, data.get('garage_spaces') or None, data.get('parking_spaces') or None,
            data.get('year_built') or None, data.get('property_type'), data.get('zoning'),
            data.get('hoa_name'), data.get('hoa_dues') or None, data.get('hoa_frequency'),
            data.get('property_description'), data.get('listing_price') or None, data.get('status', 'available')
        ))
        conn.commit()
        conn.close()
        flash('Property added successfully!')
        return redirect(url_for('properties_list'))
    
    return render_template('property_form.html')

@app.route('/transactions')
def transactions_list():
    """View all transactions"""
    conn = get_db_connection()
    transactions = conn.execute('''
        SELECT t.id, t.status, t.purchase_price, t.offer_date, t.close_of_escrow_date,
               p.address_street, p.address_city, p.address_state,
               bc.first_name as buyer_first, bc.last_name as buyer_last,
               sc.first_name as seller_first, sc.last_name as seller_last
        FROM transactions t
        JOIN properties p ON t.property_id = p.id
        LEFT JOIN clients bc ON t.buyer_client_id = bc.id
        LEFT JOIN clients sc ON t.seller_client_id = sc.id
        ORDER BY t.created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('transactions_list.html', transactions=transactions)

@app.route('/transactions/new', methods=['GET', 'POST'])
def new_transaction():
    """Create new transaction"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.form
        
        # Handle boolean checkboxes
        bool_fields = [
            'financing_contingency', 'inspection_contingency', 'appraisal_contingency',
            'title_contingency', 'sale_of_property_contingency', 'homeowners_insurance_contingency',
            'hoa_approval_contingency', 'as_is_sale', 'seller_financing'
        ]
        
        conn.execute('''
            INSERT INTO transactions (
                property_id, buyer_client_id, seller_client_id, transaction_type,
                purchase_price, earnest_money_amount, down_payment_amount, down_payment_percentage,
                loan_amount, loan_term_years, interest_rate, offer_date, acceptance_date,
                contract_date, close_of_escrow_date, possession_date, inspection_deadline,
                appraisal_deadline, loan_approval_deadline, contingency_removal_date,
                financing_contingency, inspection_contingency, appraisal_contingency,
                title_contingency, sale_of_property_contingency, homeowners_insurance_contingency,
                hoa_approval_contingency, as_is_sale, seller_financing, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['property_id'], data.get('buyer_client_id') or None, data.get('seller_client_id') or None,
            data['transaction_type'], data.get('purchase_price') or None, data.get('earnest_money_amount') or None,
            data.get('down_payment_amount') or None, data.get('down_payment_percentage') or None,
            data.get('loan_amount') or None, data.get('loan_term_years') or None, data.get('interest_rate') or None,
            data.get('offer_date') or None, data.get('acceptance_date') or None, data.get('contract_date') or None,
            data.get('close_of_escrow_date') or None, data.get('possession_date') or None,
            data.get('inspection_deadline') or None, data.get('appraisal_deadline') or None,
            data.get('loan_approval_deadline') or None, data.get('contingency_removal_date') or None,
            'financing_contingency' in data, 'inspection_contingency' in data, 'appraisal_contingency' in data,
            'title_contingency' in data, 'sale_of_property_contingency' in data, 'homeowners_insurance_contingency' in data,
            'hoa_approval_contingency' in data, 'as_is_sale' in data, 'seller_financing' in data,
            data.get('notes')
        ))
        conn.commit()
        conn.close()
        flash('Transaction created successfully!')
        return redirect(url_for('transactions_list'))
    
    # Get clients and properties for dropdowns
    clients = conn.execute('SELECT id, first_name, last_name, client_type FROM clients ORDER BY last_name, first_name').fetchall()
    properties = conn.execute('SELECT id, address_street, address_city, address_state FROM properties WHERE status = "available" ORDER BY address_city').fetchall()
    conn.close()
    
    return render_template('transaction_form.html', clients=clients, properties=properties)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages from the AI chatbot"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message']
        print(f"[CHAT] Received message: {user_message}")
        
        # Get AI response from Gemini API
        ai_response = get_gemini_response(user_message)
        
        print(f"[CHAT] AI responding with: {ai_response[:100]}...")
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().isoformat(),
            'model': 'gemini-pro'
        })
        
    except Exception as e:
        print(f"[CHAT ERROR] {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/process_email', methods=['POST'])
def process_email():
    """Handle email processing requests from the chatbot"""
    try:
        data = request.get_json()
        if not data or 'email_content' not in data:
            return jsonify({'error': 'No email content provided'}), 400
        
        email_content = data['email_content']
        print(f"[EMAIL PROCESSING] Received content length: {len(email_content)} characters")
        print(f"[EMAIL PROCESSING] Content preview: {email_content[:200]}...")
        
        # For now, log the email content and return a placeholder response
        # TODO: Implement data mapping and CRM integration in Task #6
        extracted_data = {
            'status': 'received',
            'content_length': len(email_content),
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"[EMAIL PROCESSING] Extracted data: {extracted_data}")
        
        return jsonify({
            'extracted_data': extracted_data,
            'message': 'Email received and logged successfully'
        })
        
    except Exception as e:
        print(f"[EMAIL PROCESSING ERROR] {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/generate_forms/<int:transaction_id>')
def generate_forms(transaction_id):
    """Generate PDF forms for a transaction"""
    conn = get_db_connection()
    
    # Get complete transaction data
    transaction_data = conn.execute('''
        SELECT t.*, p.*, 
               bc.first_name as buyer_first, bc.last_name as buyer_last, bc.email as buyer_email,
               bc.phone_primary as buyer_phone, bc.address_street as buyer_address,
               bc.address_city as buyer_city, bc.address_state as buyer_state, bc.address_zip as buyer_zip,
               sc.first_name as seller_first, sc.last_name as seller_last, sc.email as seller_email,
               sc.phone_primary as seller_phone
        FROM transactions t
        JOIN properties p ON t.property_id = p.id
        LEFT JOIN clients bc ON t.buyer_client_id = bc.id
        LEFT JOIN clients sc ON t.seller_client_id = sc.id
        WHERE t.id = ?
    ''', (transaction_id,)).fetchone()
    
    conn.close()
    
    if not transaction_data:
        return jsonify({'error': 'Transaction not found'}), 404
    
    # Convert to dict for JSON serialization
    data = dict(transaction_data)
    
    # TODO: Integrate with existing PDF generation modules
    # This would call your professional_pdf_filler.py or similar
    
    return jsonify({
        'message': 'Forms generation initiated',
        'transaction_id': transaction_id,
        'data': data
    }, cls=DateTimeEncoder)

if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)