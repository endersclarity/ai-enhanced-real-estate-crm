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

# Import ZipForm functions
try:
    from zipform_ai_functions import (
        create_client_zipform, create_property_zipform, create_transaction,
        create_broker_agent, create_lender, create_title_company, 
        create_escrow_company, create_service_provider, ZIPFORM_AI_FUNCTIONS
    )
    ZIPFORM_AVAILABLE = True
except ImportError:
    print("⚠️  ZipForm functions not available - run migration first")
    ZIPFORM_AVAILABLE = False

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change in production

DATABASE_PATH = 'database/real_estate.db'

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

# Load MLS data on startup
def load_mls_on_startup():
    """Load MLS data when Flask starts up"""
    try:
        from mls_integration import load_mls_data
        mls_file = 'Listing.csv'  # Use the main MLS file with 526 listings
        if os.path.exists(mls_file):
            result = load_mls_data(mls_file)
            if result['success']:
                print(f"✅ MLS data loaded: {result['count']} listings from {mls_file}")
            else:
                print(f"⚠️  MLS load failed: {result['message']}")
        else:
            print(f"⚠️  MLS file not found: {mls_file}")
    except Exception as e:
        print(f"⚠️  MLS startup error: {str(e)}")

# Load MLS data
load_mls_on_startup()

def get_available_functions():
    """
    Get all available AI-callable functions with descriptions
    
    Returns:
        dict: Function registry with descriptions and usage examples
    """
    functions = {}
    
    # Core CRM Functions
    functions.update(AI_CALLABLE_FUNCTIONS)
    
    # Add ZipForm Functions if available
    try:
        from streamlined_zipform_functions import STREAMLINED_ZIPFORM_FUNCTIONS
        functions.update(STREAMLINED_ZIPFORM_FUNCTIONS)
    except ImportError:
        pass
    
    # Add MLS Functions if available
    try:
        from mls_integration import MLS_FUNCTIONS
        functions.update(MLS_FUNCTIONS)
    except ImportError:
        pass
    
    return functions

def extract_client_data_from_message(message):
    """
    Extract client data from natural language message using regex patterns
    
    Args:
        message (str): User message containing client information
        
    Returns:
        dict: Extracted client data or None if insufficient data
    """
    import re
    
    # Initialize extracted data
    extracted = {}
    
    # Name patterns - prioritize clean name extraction
    name_patterns = [
        r'create\s+(?:client|contact):\s*([A-Za-z]+)\s+([A-Za-z]+)',  # "create client: John Smith"
        r'name\s+is\s+([A-Za-z]+)\s+([A-Za-z]+)',                     # "my name is Jennifer Martinez"
        r'Full\s+Name[:\s]+([A-Za-z]+)\s+([A-Za-z]+)',               # "Full Name: Jennifer Martinez"
        r'^([A-Za-z]+)\s+([A-Za-z]+),?\s+email',                     # "Jennifer Martinez, email:" at start
        r'([A-Za-z]+)\s+([A-Za-z]+)(?:,\s*email|.*@)',              # Name before email pattern
        r'client[:\s]+([A-Za-z]+)\s+([A-Za-z]+)'                     # "client: Jennifer Martinez"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            extracted['first_name'] = match.group(1)
            extracted['last_name'] = match.group(2)
            break
    
    # Email pattern
    email_match = re.search(r'email[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', message, re.IGNORECASE)
    if email_match:
        extracted['email'] = email_match.group(1)
    
    # Phone pattern
    phone_match = re.search(r'phone[:\s]*(\([0-9]{3}\)\s*[0-9]{3}-[0-9]{4}|\([0-9]{3}\)\s*[0-9]{3}\s*[0-9]{4}|[0-9]{3}-[0-9]{3}-[0-9]{4})', message, re.IGNORECASE)
    if phone_match:
        extracted['phone'] = phone_match.group(1)
    
    # Client type detection
    if any(word in message.lower() for word in ['buyer', 'buying', 'purchase', 'looking to buy']):
        extracted['client_type'] = 'buyer'
    elif any(word in message.lower() for word in ['seller', 'selling', 'list', 'listing']):
        extracted['client_type'] = 'seller'
    else:
        extracted['client_type'] = 'buyer'  # Default
    
    # Address pattern
    address_match = re.search(r'address[:\s]*([^,\n]+)', message, re.IGNORECASE)
    if address_match:
        address_parts = address_match.group(1).strip().split(',')
        if len(address_parts) >= 1:
            extracted['street_address'] = address_parts[0].strip()
        if len(address_parts) >= 2:
            extracted['city'] = address_parts[1].strip()
        if len(address_parts) >= 3:
            state_zip = address_parts[2].strip().split()
            if len(state_zip) >= 1:
                extracted['state'] = state_zip[0]
            if len(state_zip) >= 2:
                extracted['zip_code'] = state_zip[1]
    
    # Only return if we have essential data (name and either email or phone)
    if ('first_name' in extracted and 'last_name' in extracted and 
        ('email' in extracted or 'phone' in extracted)):
        return extracted
    
    return None

def build_ai_context():
    """
    Build comprehensive AI context with CRM function awareness
    
    Returns:
        str: Enhanced system prompt with function awareness
    """
    available_functions = get_available_functions()
    
    # Build function documentation
    function_docs = []
    for func_name, func_info in available_functions.items():
        func_doc = f"""
{func_name}:
  Description: {func_info.get('description', 'No description')}
  Required: {', '.join(func_info.get('required_params', []))}
  Optional: {', '.join(func_info.get('optional_params', [])[:5])}{'...' if len(func_info.get('optional_params', [])) > 5 else ''}
  Example: {func_info.get('example', 'No example')}"""
        function_docs.append(func_doc)
    
    system_prompt = f"""You are an intelligent Real Estate CRM Assistant for Narissa Realty. You excel at understanding casual conversation and inferring what database actions would be helpful.

🧠 CONVERSATIONAL INTELLIGENCE:
You understand real estate agent casual talk and can infer database operations from natural conversation. When someone mentions clients, properties, or business activities, you intelligently propose relevant CRM actions.

🎯 CORE BEHAVIOR:
1. **LISTEN CAREFULLY** to what users say about their real estate business
2. **INFER ACTIONS** - What database operations would help based on their words?
3. **PROPOSE CLEARLY** - "I can create a client record for John with this info..."
4. **EXTRACT DATA** - Pull names, phones, emails, addresses, preferences from conversation
5. **CONFIRM FIRST** - Always ask permission before any database operations

🤖 AVAILABLE DATABASE OPERATIONS:
{chr(10).join(function_docs[:8])}

💬 CONVERSATION EXAMPLES:

User: "Just met Sarah Williams at the open house, she's looking for a 3BR under $500K in Grass Valley, her cell is 916-555-0123"
You: "I can create a client record for Sarah Williams with:
- Name: Sarah Williams  
- Phone: 916-555-0123
- Type: Buyer
- Budget: Under $500K
- Area preference: Grass Valley
- Bedrooms: 3+
- Lead source: Open house
Should I add her to the CRM?"

User: "Christopher Brown called, his email changed to chris.brown.new@gmail.com and his budget went up to $650K"
You: "I found Christopher Brown in your CRM. I can update his record with:
- New email: chris.brown.new@gmail.com  
- Updated budget: $650,000
Should I make these changes?"

User: "That property on Pine Street sold for $625K, need to update the status"
You: "I can search for the Pine Street property and update its status to sold with a sale price of $625,000. Which Pine Street property? Do you have the address or MLS number?"

🔍 ENTITY EXTRACTION:
Always extract: Names, phones, emails, addresses, prices, dates, preferences, property features, lead sources, notes

🚨 SAFETY RULES:
- NEVER execute database operations without explicit user confirmation
- ALWAYS show exactly what you plan to do before doing it
- Ask clarifying questions if information is unclear
- Propose the most helpful action based on context

Be conversational, intuitive, and focus on making the agent's life easier by intelligently managing their CRM data."""
    
    return system_prompt

def get_gemini_response(message, context="", conversation_history=None):
    """
    Enhanced AI response with CRM function awareness and conversation memory
    
    Args:
        message (str): User message
        context (str): Additional context (optional)
        conversation_history (list): Previous messages for context
    
    Returns:
        dict: {'response': str, 'suggested_functions': list, 'confidence': float}
    """
    if not GEMINI_CONFIGURED:
        return {
            'response': "AI service is currently unavailable. Please check configuration.",
            'suggested_functions': [],
            'confidence': 0.0
        }
    
    try:
        # Use LangChain approach (like Langchain8n project)
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage, SystemMessage
        
        llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash-preview-04-17",
            google_api_key=GEMINI_API_KEY,
            temperature=0.1
        )
        
        # Build enhanced system prompt with function awareness
        system_prompt = build_ai_context()
        
        # Add conversation context if provided
        if context:
            system_prompt += f"\n\n🎯 CURRENT CONTEXT: {context}"
        
        # Build message history
        messages = [SystemMessage(content=system_prompt)]
        
        # Add conversation history if provided
        if conversation_history:
            for hist_msg in conversation_history[-5:]:  # Last 5 messages for context
                if hist_msg.get('role') == 'user':
                    messages.append(HumanMessage(content=hist_msg['content']))
                elif hist_msg.get('role') == 'assistant':
                    messages.append(SystemMessage(content=f"Previous AI response: {hist_msg['content'][:200]}..."))
        
        # Add current user message
        messages.append(HumanMessage(content=message))
        
        # Generate response
        response = llm.invoke(messages)
        
        # Analyze response for function suggestions
        suggested_functions = analyze_response_for_functions(response.content, message)
        
        return {
            'response': response.content,
            'suggested_functions': suggested_functions,
            'confidence': calculate_response_confidence(response.content, message)
        }
        
    except Exception as e:
        print(f"[GEMINI API ERROR] {str(e)}")
        return {
            'response': f"I apologize, but I'm experiencing technical difficulties. Please try again later. (Error: {str(e)[:50]}...)",
            'suggested_functions': [],
            'confidence': 0.0
        }

def analyze_response_for_functions(ai_response, user_message):
    """
    Analyze AI response to detect when it's proposing database operations
    
    Args:
        ai_response (str): AI's response text
        user_message (str): Original user message
    
    Returns:
        list: Detected database operation proposals with extracted data
    """
    suggestions = []
    import re
    
    # Enhanced patterns to detect AI proposals
    proposal_patterns = [
        r"I can create a client record for ([^\n]+)",
        r"I can update ([^']+)'s record",
        r"I can add ([^\s]+) to the CRM",
        r"Should I (create|add|update) ([^?]+)\?",
        r"I can search for ([^\n]+) and update"
    ]
    
    for pattern in proposal_patterns:
        matches = re.findall(pattern, ai_response, re.IGNORECASE)
        if matches:
            # AI is proposing an operation - extract the details
            proposal_data = extract_entities_from_text(f"{user_message} {ai_response}")
            
            if proposal_data:
                suggestions.append({
                    'function': determine_operation_type(ai_response, proposal_data),
                    'parameters': proposal_data,
                    'reason': 'AI proposed database operation',
                    'confidence': 0.9,
                    'proposal_text': matches[0] if isinstance(matches[0], str) else str(matches[0])
                })
    
    return suggestions

def extract_entities_from_text(text):
    """
    Extract CRM entities from text using regex patterns
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Extracted entity data
    """
    import re
    
    entities = {}
    
    # Name patterns - look for "Name: Value" or mentions after key phrases
    name_patterns = [
        r"(?:client record for|add|create client)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
        r"Name:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)",
        r"([A-Z][a-z]+\s+[A-Z][a-z]+)(?:'s record|\s+called|\s+at the)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            full_name = match.group(1).strip()
            name_parts = full_name.split()
            if len(name_parts) >= 2:
                entities['first_name'] = name_parts[0]
                entities['last_name'] = ' '.join(name_parts[1:])
            break
    
    # Phone patterns
    phone_match = re.search(r"(?:phone|cell|number)[:\s]*([\\(]?\d{3}[\\)]?[\s.-]?\d{3}[\s.-]?\d{4})", text, re.IGNORECASE)
    if phone_match:
        entities['phone'] = phone_match.group(1)
    
    # Email patterns  
    email_match = re.search(r"(?:email)[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", text, re.IGNORECASE)
    if email_match:
        entities['email'] = email_match.group(1)
    
    # Budget/price patterns
    budget_match = re.search(r"(?:budget|under|up to)[:\s]*\$?([\d,]+)K?", text, re.IGNORECASE)
    if budget_match:
        budget_str = budget_match.group(1).replace(',', '')
        if 'K' in budget_match.group(0):
            entities['budget'] = int(budget_str) * 1000
        else:
            entities['budget'] = int(budget_str)
    
    # Area/location preferences
    area_match = re.search(r"(?:in|looking in|area preference)[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text, re.IGNORECASE)
    if area_match:
        entities['area_preference'] = area_match.group(1)
    
    # Bedrooms
    bedroom_match = re.search(r"(\d+)BR|bedrooms[:\s]*(\d+)", text, re.IGNORECASE)
    if bedroom_match:
        entities['bedrooms'] = int(bedroom_match.group(1) or bedroom_match.group(2))
    
    # Client type inference
    if any(word in text.lower() for word in ['looking for', 'buyer', 'buying', 'purchase']):
        entities['client_type'] = 'buyer'
    elif any(word in text.lower() for word in ['selling', 'seller', 'list', 'listing']):
        entities['client_type'] = 'seller'
    else:
        entities['client_type'] = 'buyer'  # Default
    
    return entities if entities else None

def determine_operation_type(ai_response, entities):
    """
    Determine what type of database operation the AI is proposing
    """
    response_lower = ai_response.lower()
    
    if 'create' in response_lower and 'client' in response_lower:
        return 'create_client'
    elif 'update' in response_lower and 'record' in response_lower:
        return 'update_client'
    elif 'create' in response_lower and 'property' in response_lower:
        return 'create_property'
    elif 'search' in response_lower and 'property' in response_lower:
        return 'find_properties'
    else:
        return 'create_client'  # Default to client creation

def calculate_response_confidence(ai_response, user_message):
    """
    Calculate confidence in AI response based on content analysis
    
    Args:
        ai_response (str): AI response
        user_message (str): User message
    
    Returns:
        float: Confidence score (0.0 to 1.0)
    """
    confidence = 0.5  # Base confidence
    
    # Increase confidence for specific real estate terms
    real_estate_terms = ['client', 'property', 'listing', 'transaction', 'mls', 'offer', 'buyer', 'seller']
    term_matches = sum(1 for term in real_estate_terms if term in ai_response.lower())
    confidence += min(term_matches * 0.1, 0.3)
    
    # Increase confidence for function suggestions
    if 'suggest' in ai_response.lower() or 'recommend' in ai_response.lower():
        confidence += 0.1
    
    # Decrease confidence for error indicators
    if any(error in ai_response.lower() for error in ['error', 'sorry', 'unable', 'cannot']):
        confidence -= 0.2
    
    return min(max(confidence, 0.0), 1.0)

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
                first_name, last_name, email, home_phone, client_type,
                business_phone, street_address, city, 
                state, zip_code, employer, occupation, annual_income,
                ssn_last_four, preferred_contact_method, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            first_name, last_name, email, phone, client_type,
            kwargs.get('business_phone'), kwargs.get('street_address'), 
            kwargs.get('city'), kwargs.get('state'), kwargs.get('zip_code'),
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
            SELECT id, first_name, last_name, email, home_phone, client_type,
                   address_city, address_state, created_at
            FROM clients
            WHERE 1=1
        '''
        params = []
        
        if search_term:
            query += ''' AND (
                first_name LIKE ? OR last_name LIKE ? OR 
                email LIKE ? OR home_phone LIKE ?
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
                'phone': client['home_phone'],
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
            'first_name', 'last_name', 'email', 'home_phone', 
            'business_phone', 'client_type', 'street_address', 'city',
            'state', 'zip_code', 'employer', 'occupation', 'annual_income',
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

# Enhanced function registry for AI discovery (includes both legacy and ZipForm functions)
AI_CALLABLE_FUNCTIONS = {
    # Legacy functions (for backward compatibility)
    'create_client': {
        'function': create_client,
        'description': 'Create a new client with basic contact information (legacy)',
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
        'optional_params': ['first_name', 'last_name', 'email', 'home_phone', 'address_street'],
        'example': 'update_client(123, email="newemail@example.com", home_phone="555-9999")'
    },
    'create_property': {
        'function': create_property,
        'description': 'Add a new property listing to the system (legacy)',
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

# Add ZipForm functions if available
if ZIPFORM_AVAILABLE:
    AI_CALLABLE_FUNCTIONS.update(ZIPFORM_AI_FUNCTIONS)
    print("✅ ZipForm AI functions loaded successfully")
else:
    print("⚠️  Running with legacy functions only")

@app.route('/')
def dashboard():
    """Main dashboard view"""
    conn = get_db_connection()
    
    # Get dashboard statistics
    stats = {
        'total_clients': conn.execute('SELECT COUNT(*) as count FROM clients').fetchone()['count'],
        'active_transactions': conn.execute('SELECT COUNT(*) as count FROM transactions WHERE status IN ("pending", "in_progress", "under_contract")').fetchone()['count'],
        'properties': conn.execute('SELECT COUNT(*) as count FROM properties').fetchone()['count'],
        'this_month_closings': 0  # Simplified for now
    }
    
    # Get recent transactions
    # Get recent transactions (simplified query to avoid schema issues)
    try:
        recent_transactions = conn.execute('''
            SELECT t.id, t.status, t.purchase_price, t.offer_date, 
                   'Address TBD' as address_street, 'City TBD' as address_city,
                   'Buyer TBD' as buyer_first, '' as buyer_last,
                   'Seller TBD' as seller_first, '' as seller_last
            FROM transactions t
            ORDER BY t.created_at DESC
            LIMIT 10
        ''').fetchall()
    except:
        # Fallback to empty list if transactions table has issues
        recent_transactions = []
    
    conn.close()
    return render_template('crm_dashboard.html', stats=stats, recent_transactions=recent_transactions)

@app.route('/debug_chat')
def debug_chat():
    """Debug chat interface for testing chatbot functionality"""
    return render_template('debug_chat.html')

@app.route('/clients')
def clients_list():
    """View all clients"""
    conn = get_db_connection()
    clients = conn.execute('''
        SELECT id, client_type, first_name, last_name, email, home_phone, 
               city, state, created_at
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
                client_type, first_name, last_name, middle_initial, email, home_phone,
                business_phone, street_address, city, state, zip_code,
                employer, occupation, annual_income, ssn_last_four, preferred_contact_method, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['client_type'], data['first_name'], data['last_name'], data.get('middle_initial'),
            data.get('email'), data.get('home_phone'), data.get('business_phone'),
            data.get('street_address'), data.get('city'), data.get('state'),
            data.get('zip_code'), data.get('employer'), data.get('occupation'),
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
        SELECT t.*, p.street_address, p.city, p.state
        FROM transactions t
        JOIN properties p ON t.property_id = p.id
        WHERE t.buyer_client_id = ? OR t.seller_client_id = ?
        ORDER BY t.created_at DESC
    ''', (client_id, client_id)).fetchall()
    
    conn.close()
    return render_template('client_detail.html', client=client, transactions=transactions)

@app.route('/properties')
def properties_list():
    """View all properties with search functionality"""
    conn = get_db_connection()
    
    # Get search parameters
    search = request.args.get('search', '').strip()
    property_type = request.args.get('property_type', '')
    status = request.args.get('status', '')
    city = request.args.get('city', '')
    
    # Build query with search filters
    query = '''
        SELECT id, street_address, city, state, zip_code,
               bedrooms, bathrooms, square_feet, listed_price, created_at,
               mls_number, property_type
        FROM properties 
        WHERE 1=1
    '''
    params = []
    
    if search:
        query += ''' AND (
            street_address LIKE ? OR 
            city LIKE ? OR 
            mls_number LIKE ?
        )'''
        search_pattern = f'%{search}%'
        params.extend([search_pattern, search_pattern, search_pattern])
    
    if property_type:
        query += ' AND property_type LIKE ?'
        params.append(f'%{property_type}%')
    
    if city:
        query += ' AND city LIKE ?'
        params.append(f'%{city}%')
    
    query += ' ORDER BY created_at DESC LIMIT 100'
    
    properties = conn.execute(query, params).fetchall()
    
    # Get unique cities for dropdown
    cities = conn.execute('SELECT DISTINCT city FROM properties WHERE city IS NOT NULL ORDER BY city').fetchall()
    
    conn.close()
    
    return render_template('properties_list.html', 
                         properties=properties, 
                         cities=cities,
                         search=search,
                         property_type=property_type,
                         city=city)

@app.route('/properties/new', methods=['GET', 'POST'])
def new_property():
    """Add new property"""
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO properties (
                street_address, city, state, zip_code, county,
                assessor_parcel_number, lot_number, subdivision, lot_size_sqft, lot_size_acres,
                square_feet, bedrooms, bathrooms, year_built, property_type,
                property_description, listed_price
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['street_address'], data['city'], data['state'], data['zip_code'],
            data.get('county'), data.get('assessor_parcel_number'), data.get('lot_number'), data.get('subdivision'),
            data.get('lot_size_sqft') or None, data.get('lot_size_acres') or None,
            data.get('square_feet') or None, data.get('bedrooms') or None, data.get('bathrooms') or None,
            data.get('year_built') or None, data.get('property_type'),
            data.get('property_description'), data.get('listed_price') or None
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
        SELECT t.id, t.status, t.purchase_price, t.offer_date, t.closing_date,
               p.street_address, p.city, p.state,
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
    properties = conn.execute('SELECT id, street_address, city, state FROM properties ORDER BY city').fetchall()
    conn.close()
    
    return render_template('transaction_form.html', clients=clients, properties=properties)

@app.route('/chat', methods=['POST'])
def chat():
    """Enhanced AI chatbot with CRM function awareness and conversation memory"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message']
        conversation_history = data.get('conversation_history', [])
        current_context = data.get('context', '')
        
        print(f"[CHAT] Enhanced AI processing: {user_message[:50]}...")
        
        # Get enhanced AI response with CRM function awareness
        ai_result = get_gemini_response(
            message=user_message,
            context=current_context,
            conversation_history=conversation_history
        )
        
        # Smart analysis: detect when AI proposes database operations
        proposed_operations = []
        suggested_functions = ai_result.get('suggested_functions', [])
        
        # Enhanced detection for AI proposals using new analysis functions
        for suggestion in suggested_functions:
            if suggestion.get('confidence', 0) >= 0.8 and suggestion.get('parameters'):
                # AI proposed a database operation with extracted data
                operation_id = f"op_{int(datetime.now().timestamp())}_{suggestion['function']}"
                
                # Store the proposed operation for user confirmation
                pending_operations[operation_id] = {
                    'operation_type': suggestion['function'],
                    'operation_data': suggestion['parameters'],
                    'context': 'AI Smart Analysis',
                    'user_message': user_message,
                    'ai_response': ai_result['response'],
                    'status': 'pending_confirmation',
                    'created_at': datetime.now().isoformat(),
                    'ai_confidence': suggestion.get('confidence', 0),
                    'proposal_text': suggestion.get('proposal_text', '')
                }
                
                proposed_operations.append({
                    'operation_id': operation_id,
                    'type': suggestion['function'],
                    'data': suggestion['parameters'],
                    'confidence': suggestion.get('confidence', 0),
                    'proposal_text': suggestion.get('proposal_text', ''),
                    'formatted_preview': format_operation_for_review(suggestion['function'], suggestion['parameters'])
                })
                
                print(f"[SMART PROPOSAL] {operation_id}: {suggestion['function']} with confidence {suggestion.get('confidence', 0):.2f}")
                print(f"[SMART PROPOSAL] Extracted data: {suggestion['parameters']}")
        
        # Fallback: if no smart proposals detected, try basic entity extraction
        if not proposed_operations and ai_result.get('confidence', 0) >= 0.6:
            fallback_entities = extract_entities_from_text(f"{user_message} {ai_result['response']}")
            if fallback_entities and len(fallback_entities) >= 2:  # At least 2 fields extracted
                operation_type = 'create_client'  # Default to client creation
                operation_id = f"op_{int(datetime.now().timestamp())}_fallback_{operation_type}"
                
                pending_operations[operation_id] = {
                    'operation_type': operation_type,
                    'operation_data': fallback_entities,
                    'context': 'Fallback Entity Extraction',
                    'user_message': user_message,
                    'status': 'pending_confirmation',
                    'created_at': datetime.now().isoformat(),
                    'ai_confidence': ai_result.get('confidence', 0)
                }
                
                proposed_operations.append({
                    'operation_id': operation_id,
                    'type': operation_type,
                    'data': fallback_entities,
                    'confidence': ai_result.get('confidence', 0),
                    'formatted_preview': format_operation_for_review(operation_type, fallback_entities)
                })
                
                print(f"[FALLBACK PROPOSAL] {operation_id}: Extracted {len(fallback_entities)} entities")
        
        # Build response with enhanced capabilities
        response_data = {
            'response': ai_result['response'],
            'suggested_functions': suggested_functions,
            'proposed_operations': proposed_operations,  # NEW: Auto-proposed operations
            'confidence': ai_result.get('confidence', 0.5),
            'timestamp': datetime.now().isoformat(),
            'model': 'gemini-2.5-flash-preview-04-17',
            'capabilities': {
                'function_count': len(get_available_functions()),
                'conversation_memory': len(conversation_history) > 0,
                'zipform_integration': True,
                'mls_integration': True
            }
        }
        
        # Log enhanced processing
        print(f"[ENHANCED AI] Response confidence: {ai_result.get('confidence', 0.5):.2f}")
        print(f"[ENHANCED AI] Function suggestions: {len(ai_result.get('suggested_functions', []))}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"[ENHANCED CHAT ERROR] {str(e)}")
        return jsonify({
            'error': 'AI processing error',
            'message': str(e),
            'fallback_response': 'I apologize, but I encountered an issue processing your request. Please try again.'
        }), 500

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

# ============================================================================
# USER CONFIRMATION WORKFLOW ENDPOINTS
# ============================================================================

@app.route('/propose_operation', methods=['POST'])
def propose_operation():
    """
    Propose a database operation for user confirmation.
    
    Expected payload:
    {
        "operation_type": "create_client|update_client|create_property|etc.",
        "operation_data": {...},
        "context": "Email processing|Chat request|etc.",
        "user_message": "Original user request"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No operation data provided'}), 400
        
        operation_type = data.get('operation_type')
        operation_data = data.get('operation_data', {})
        context = data.get('context', 'Manual request')
        user_message = data.get('user_message', '')
        
        if not operation_type:
            return jsonify({'error': 'Operation type is required'}), 400
        
        # Validate operation type
        valid_operations = [
            'create_client', 'update_client', 'find_clients',
            'create_property', 'update_property', 'find_properties',
            'create_transaction', 'update_transaction',
            'schedule_showing', 'add_note'
        ]
        
        if operation_type not in valid_operations:
            return jsonify({'error': f'Invalid operation type: {operation_type}'}), 400
        
        # Generate unique operation ID for tracking
        operation_id = f"op_{int(datetime.now().timestamp())}_{operation_type}"
        
        # Store pending operation (in production, this would be Redis or database)
        pending_operations[operation_id] = {
            'operation_type': operation_type,
            'operation_data': operation_data,
            'context': context,
            'user_message': user_message,
            'proposed_at': datetime.now().isoformat(),
            'status': 'pending_confirmation'
        }
        
        print(f"[OPERATION PROPOSAL] {operation_id}: {operation_type} with {len(operation_data)} fields")
        
        # Format operation for user review
        formatted_operation = format_operation_for_review(operation_type, operation_data)
        
        return jsonify({
            'operation_id': operation_id,
            'operation_type': operation_type,
            'formatted_operation': formatted_operation,
            'operation_data': operation_data,
            'context': context,
            'user_message': user_message,
            'requires_confirmation': True,
            'estimated_impact': analyze_operation_impact(operation_type, operation_data)
        })
        
    except Exception as e:
        print(f"[OPERATION PROPOSAL ERROR] {str(e)}")
        return jsonify({'error': 'Failed to propose operation'}), 500

@app.route('/confirm_operation', methods=['POST'])
def confirm_operation():
    """
    Execute a confirmed database operation.
    
    Expected payload:
    {
        "operation_id": "op_...",
        "confirmed": true|false,
        "modified_data": {...} // Optional: user modifications to the proposed data
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No confirmation data provided'}), 400
        
        operation_id = data.get('operation_id')
        confirmed = data.get('confirmed', False)
        modified_data = data.get('modified_data', {})
        
        if not operation_id:
            return jsonify({'error': 'Operation ID is required'}), 400
        
        # Retrieve pending operation
        if operation_id not in pending_operations:
            print(f"[DEBUG CONFIRM ERROR] Operation {operation_id} not found in pending_operations")
            print(f"[DEBUG CONFIRM ERROR] Available operations: {list(pending_operations.keys())}")
            return jsonify({'error': 'Operation not found or expired'}), 404
        
        operation = pending_operations[operation_id]
        
        # 🚨 CRITICAL DEBUG: Log what we're retrieving from storage
        print(f"[DEBUG CONFIRM RETRIEVAL] Operation ID: {operation_id}")
        print(f"[DEBUG CONFIRM RETRIEVAL] Retrieved operation_type: {operation['operation_type']}")
        print(f"[DEBUG CONFIRM RETRIEVAL] Retrieved operation_data: {operation['operation_data']}")
        print(f"[DEBUG CONFIRM RETRIEVAL] User confirmed: {confirmed}")
        print(f"[DEBUG CONFIRM RETRIEVAL] Modified data provided: {modified_data}")
        
        if not confirmed:
            # User rejected the operation
            operation['status'] = 'rejected'
            operation['rejected_at'] = datetime.now().isoformat()
            print(f"[OPERATION REJECTED] {operation_id}: {operation['operation_type']}")
            
            return jsonify({
                'operation_id': operation_id,
                'status': 'rejected',
                'message': 'Operation cancelled by user'
            })
        
        # User confirmed - execute the operation
        operation_type = operation['operation_type']
        
        # Use modified data if provided, otherwise use original
        execution_data = modified_data if modified_data else operation['operation_data']
        
        # 🚨 CRITICAL DEBUG: Log data flow right before execution
        print(f"[DEBUG PRE-EXECUTION] About to execute operation")
        print(f"[DEBUG PRE-EXECUTION] Operation Type: {operation_type}")
        print(f"[DEBUG PRE-EXECUTION] Execution Data: {execution_data}")
        print(f"[DEBUG PRE-EXECUTION] Original operation_data from storage: {operation['operation_data']}")
        print(f"[DEBUG PRE-EXECUTION] Modified data from user: {modified_data}")
        
        # Execute the actual database operation
        result = execute_database_operation(operation_type, execution_data)
        
        # Update operation status
        operation['status'] = 'completed' if result['success'] else 'failed'
        operation['executed_at'] = datetime.now().isoformat()
        operation['execution_result'] = result
        operation['final_data'] = execution_data
        
        print(f"[OPERATION EXECUTED] {operation_id}: {operation_type} -> {'SUCCESS' if result['success'] else 'FAILED'}")
        
        # Clean up completed operation (optional - could keep for audit)
        if result['success']:
            del pending_operations[operation_id]
        
        return jsonify({
            'operation_id': operation_id,
            'status': 'completed' if result['success'] else 'failed',
            'result': result,
            'execution_data': execution_data,
            'message': result.get('message', 'Operation completed')
        })
        
    except Exception as e:
        print(f"[OPERATION CONFIRMATION ERROR] {str(e)}")
        return jsonify({'error': 'Failed to execute operation'}), 500

@app.route('/pending_operations', methods=['GET'])
def get_pending_operations():
    """Get all pending operations for the current session"""
    try:
        # Filter out expired operations (older than 1 hour)
        current_time = datetime.now()
        active_operations = {}
        
        for op_id, operation in pending_operations.items():
            proposed_time = datetime.fromisoformat(operation['proposed_at'])
            if (current_time - proposed_time).total_seconds() < 3600:  # 1 hour
                active_operations[op_id] = operation
        
        # Update the global dict to remove expired operations
        pending_operations.clear()
        pending_operations.update(active_operations)
        
        return jsonify({
            'pending_operations': active_operations,
            'count': len(active_operations)
        })
        
    except Exception as e:
        print(f"[PENDING OPERATIONS ERROR] {str(e)}")
        return jsonify({'error': 'Failed to retrieve pending operations'}), 500

@app.route('/debug/pending_operations', methods=['GET'])
def debug_pending_operations():
    """Enhanced debug endpoint to inspect pending operations in detail"""
    try:
        debug_info = {
            'timestamp': datetime.now().isoformat(),
            'total_operations': len(pending_operations),
            'pending_operations_detailed': {}
        }
        
        for op_id, operation in pending_operations.items():
            debug_info['pending_operations_detailed'][op_id] = {
                'operation_type': operation.get('operation_type'),
                'operation_data': operation.get('operation_data'),
                'user_message': operation.get('user_message', '')[:100] + '...',
                'status': operation.get('status'),
                'created_at': operation.get('created_at'),
                'ai_confidence': operation.get('ai_confidence')
            }
        
        print(f"[DEBUG ENDPOINT] Pending operations dump: {debug_info}")
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({'error': f'Debug failed: {str(e)}'}), 500

# ============================================================================
# HELPER FUNCTIONS FOR CONFIRMATION WORKFLOW
# ============================================================================

def format_operation_for_review(operation_type, operation_data):
    """Format operation data for user-friendly review"""
    if operation_type == 'create_client':
        return {
            'title': 'Create New Client',
            'description': f"Add {operation_data.get('first_name', '')} {operation_data.get('last_name', '')} to CRM",
            'fields': [
                {'label': 'Name', 'value': f"{operation_data.get('first_name', '')} {operation_data.get('last_name', '')}", 'key': 'name'},
                {'label': 'Email', 'value': operation_data.get('email', 'Not provided'), 'key': 'email'},
                {'label': 'Phone', 'value': operation_data.get('phone', 'Not provided'), 'key': 'phone'},
                {'label': 'Type', 'value': operation_data.get('client_type', 'buyer'), 'key': 'client_type'},
                {'label': 'Source', 'value': operation_data.get('lead_source', 'Email/Chat'), 'key': 'lead_source'}
            ]
        }
    elif operation_type == 'create_property':
        return {
            'title': 'Create New Property',
            'description': f"Add property at {operation_data.get('address_street', 'Address TBD')}",
            'fields': [
                {'label': 'Address', 'value': operation_data.get('address_street', 'TBD'), 'key': 'address_street'},
                {'label': 'City', 'value': operation_data.get('address_city', 'TBD'), 'key': 'address_city'},
                {'label': 'Price', 'value': f"${operation_data.get('list_price', 'TBD')}" if operation_data.get('list_price') else 'TBD', 'key': 'list_price'},
                {'label': 'Bedrooms', 'value': operation_data.get('bedrooms', 'TBD'), 'key': 'bedrooms'},
                {'label': 'Bathrooms', 'value': operation_data.get('bathrooms', 'TBD'), 'key': 'bathrooms'},
                {'label': 'Square Feet', 'value': operation_data.get('square_feet', 'TBD'), 'key': 'square_feet'}
            ]
        }
    elif operation_type == 'create_transaction':
        return {
            'title': 'Create New Transaction',
            'description': f"Start transaction for {operation_data.get('property_address', 'property')}",
            'fields': [
                {'label': 'Property', 'value': operation_data.get('property_address', 'TBD'), 'key': 'property_address'},
                {'label': 'Buyer', 'value': operation_data.get('buyer_name', 'TBD'), 'key': 'buyer_name'},
                {'label': 'Seller', 'value': operation_data.get('seller_name', 'TBD'), 'key': 'seller_name'},
                {'label': 'Purchase Price', 'value': f"${operation_data.get('purchase_price', 'TBD')}" if operation_data.get('purchase_price') else 'TBD', 'key': 'purchase_price'},
                {'label': 'Status', 'value': operation_data.get('status', 'pending'), 'key': 'status'}
            ]
        }
    else:
        # Generic formatting for other operations
        return {
            'title': operation_type.replace('_', ' ').title(),
            'description': f"Execute {operation_type} operation",
            'fields': [
                {'label': key.replace('_', ' ').title(), 'value': str(value), 'key': key}
                for key, value in operation_data.items()
            ]
        }

def analyze_operation_impact(operation_type, operation_data):
    """Analyze the potential impact of an operation"""
    impact = {
        'risk_level': 'low',
        'affected_records': 1,
        'reversible': True,
        'warnings': []
    }
    
    if operation_type in ['create_client', 'create_property', 'create_transaction']:
        impact['risk_level'] = 'low'
        impact['affected_records'] = 1
        impact['reversible'] = True
    elif operation_type.startswith('update_'):
        impact['risk_level'] = 'medium'
        impact['affected_records'] = 1
        impact['reversible'] = False
        impact['warnings'].append('Updates cannot be automatically undone')
    elif operation_type.startswith('delete_'):
        impact['risk_level'] = 'high'
        impact['reversible'] = False
        impact['warnings'].append('Deletion is permanent and cannot be undone')
    
    return impact

def execute_database_operation(operation_type, operation_data):
    """Execute the actual database operation"""
    try:
        # 🚨 CRITICAL DEBUG: Log what's actually being executed
        print(f"[DEBUG EXECUTE] Function called: execute_database_operation")
        print(f"[DEBUG EXECUTE] Received operation_type: {operation_type}")
        print(f"[DEBUG EXECUTE] Received operation_data: {operation_data}")
        
        # Handle both legacy and ZipForm operation types
        if operation_type in ['create_client', 'create_client_zipform']:
            print(f"[DEBUG EXECUTE] Calling create_client with data: {operation_data}")
            return create_client(**operation_data)
        elif operation_type in ['update_client', 'update_client_zipform']:
            return update_client(**operation_data)
        elif operation_type in ['create_property', 'create_property_zipform']:
            return create_property(**operation_data)
        elif operation_type == 'update_property':
            return update_property(**operation_data)
        elif operation_type == 'create_transaction':
            return create_transaction(**operation_data)
        elif operation_type == 'find_clients':
            results = find_clients(**operation_data)
            return {'success': True, 'results': results, 'count': len(results)}
        else:
            return {'success': False, 'message': f'Unknown operation type: {operation_type}'}
    except Exception as e:
        return {'success': False, 'message': f'Operation failed: {str(e)}'}

# Global storage for pending operations (in production, use Redis or database)
pending_operations = {}

@app.route('/api/generate_forms/<int:transaction_id>')
def generate_forms(transaction_id):
    """Generate PDF forms for a transaction"""
    conn = get_db_connection()
    
    # Get complete transaction data
    transaction_data = conn.execute('''
        SELECT t.*, p.*, 
               bc.first_name as buyer_first, bc.last_name as buyer_last, bc.email as buyer_email,
               bc.home_phone as buyer_phone, bc.address_street as buyer_address,
               bc.address_city as buyer_city, bc.address_state as buyer_state, bc.address_zip as buyer_zip,
               sc.first_name as seller_first, sc.last_name as seller_last, sc.email as seller_email,
               sc.home_phone as seller_phone
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

@app.route('/api/dashboard_stats', methods=['GET'])
def get_dashboard_stats():
    """
    Get current dashboard statistics for real-time updates
    Implements Task 9: Real-time dashboard refresh data
    """
    try:
        conn = get_db_connection()
        
        # Get current statistics
        stats = {
            'total_clients': conn.execute('SELECT COUNT(*) as count FROM clients').fetchone()['count'],
            'active_transactions': conn.execute('SELECT COUNT(*) as count FROM transactions WHERE status IN ("pending", "in_progress", "under_contract")').fetchone()['count'],
            'properties': conn.execute('SELECT COUNT(*) as count FROM properties').fetchone()['count'],
            'this_month_closings': 0  # Simplified for now
        }
        
        # Get recent transactions with enhanced data
        try:
            recent_transactions = conn.execute('''
                SELECT t.id, t.status, t.purchase_price, t.offer_date, t.close_of_escrow_date,
                       'Address TBD' as address_street, 'City TBD' as address_city,
                       'Buyer TBD' as buyer_first, '' as buyer_last,
                       'Seller TBD' as seller_first, '' as seller_last
                FROM transactions t
                ORDER BY t.created_at DESC
                LIMIT 10
            ''').fetchall()
            
            # Convert to list of dicts for JSON serialization
            transactions_list = []
            for trans in recent_transactions:
                transactions_list.append({
                    'id': trans['id'],
                    'status': trans['status'],
                    'purchase_price': trans['purchase_price'],
                    'offer_date': trans['offer_date'],
                    'close_of_escrow_date': trans['close_of_escrow_date'],
                    'address_street': trans['address_street'],
                    'address_city': trans['address_city'],
                    'buyer_first': trans['buyer_first'],
                    'buyer_last': trans['buyer_last'],
                    'seller_first': trans['seller_first'],
                    'seller_last': trans['seller_last']
                })
        except Exception as trans_error:
            print(f"[DASHBOARD STATS] Transaction query error: {trans_error}")
            transactions_list = []
        
        conn.close()
        
        print(f"[DASHBOARD STATS] Retrieved: {stats['total_clients']} clients, {stats['properties']} properties, {len(transactions_list)} transactions")
        
        return jsonify({
            'success': True,
            'stats': stats,
            'recent_transactions': transactions_list,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[DASHBOARD STATS ERROR] {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)