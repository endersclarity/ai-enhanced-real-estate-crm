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