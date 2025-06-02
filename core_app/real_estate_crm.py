#!/usr/bin/env python3
"""
Real Estate CRM Application
Comprehensive client and transaction management for Narissa Realty
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
import sqlite3
import json
from datetime import datetime, date
from decimal import Decimal
import os
import google.generativeai as genai
from functools import wraps

# Import monitoring and SSL configuration (Tasks #9 and #10)
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
try:
    from quick_fix_monitoring import add_basic_monitoring, add_security_headers
    MONITORING_AVAILABLE = True
    print("✅ Basic monitoring and security headers loaded")
except ImportError as e:
    print(f"⚠️ Monitoring modules not available: {e}")
    MONITORING_AVAILABLE = False

# Import production configuration and database
try:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from config import current_config
    from database_config import db
    print("✅ Production configuration and Supabase database loaded")
    print(f"✅ Environment: {current_config.FLASK_ENV}")
    print(f"✅ Database: {'Supabase PostgreSQL' if current_config.USE_SUPABASE else 'SQLite'}")
    print(f"✅ AI Integration: {'Enabled' if current_config.ENABLE_AI_CHATBOT else 'Disabled'}")
    CONFIG_LOADED = True
except ImportError as e:
    print(f"⚠️ Production config not available, using fallback: {e}")
    CONFIG_LOADED = False
    
    # Fallback configuration class
    class FallbackConfig:
        FLASK_ENV = 'development'
        DEBUG = True
        HOST = '0.0.0.0'
        PORT = 5001
        SECRET_KEY = 'real-estate-crm-secret-key-2025'
        USE_SUPABASE = True
        ENABLE_AI_CHATBOT = True
        GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'your-gemini-api-key-here')
    
    current_config = FallbackConfig()
    
    # Import database with fallback
    try:
        from database_config import db
        print("✅ Database configuration loaded with fallback")
    except ImportError:
        import sqlite3
    class FallbackDB:
        def get_clients_summary(self):
            try:
                conn = sqlite3.connect('real_estate_crm.db')
                result = conn.execute('''
                    SELECT 
                        COUNT(*) as total_clients,
                        COUNT(CASE WHEN client_type = 'buyer' THEN 1 END) as buyers,
                        COUNT(CASE WHEN client_type = 'seller' THEN 1 END) as sellers,
                        COUNT(CASE WHEN status = 'active' THEN 1 END) as active_clients
                    FROM clients
                ''').fetchone()
                conn.close()
                return {
                    'total_clients': result[0] or 0,
                    'buyers': result[1] or 0,
                    'sellers': result[2] or 0,
                    'active_clients': result[3] or 0
                }
            except:
                return {'total_clients': 0, 'buyers': 0, 'sellers': 0, 'active_clients': 0}
        
        def execute_query(self, query, params=None, fetch_all=False, fetch_one=False):
            try:
                conn = sqlite3.connect('real_estate_crm.db')
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                
                if fetch_all:
                    result = cursor.fetchall()
                elif fetch_one:
                    result = cursor.fetchone()
                else:
                    conn.commit()
                    result = cursor.rowcount
                
                conn.close()
                return result
            except:
                return [] if fetch_all else None
    
    db = FallbackDB()

# Import ZipForm functions
try:
    from database.streamlined_zipform_functions import (
        create_zipform_client, create_zipform_property, create_zipform_transaction,
        create_lender, create_title_company, 
        create_escrow_company, STREAMLINED_ZIPFORM_FUNCTIONS
    )
    ZIPFORM_AVAILABLE = True
    print("✅ ZipForm AI functions loaded successfully")
except ImportError as e:
    print(f"⚠️  ZipForm functions not available: {e}")
    ZIPFORM_AVAILABLE = False

# Import Offer Creation functions
try:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from ai_modules.offer_creation_functions import (
        search_for_clients, search_for_properties, create_purchase_offer,
        get_offer_status, list_recent_offers, OFFER_CREATION_AI_FUNCTIONS
    )
    OFFER_CREATION_AVAILABLE = True
    print("✅ Offer Creation AI functions loaded successfully")
except ImportError as e:
    print(f"⚠️  Offer Creation functions not available: {e}")
    OFFER_CREATION_AVAILABLE = False

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Initialize monitoring and security (Tasks #9 and #10)
if MONITORING_AVAILABLE:
    try:
        # Initialize basic monitoring
        add_basic_monitoring(app)
        
        # Configure security headers (SSL/HTTPS)
        add_security_headers(app)
        
        print("✅ Basic monitoring initialized")
        print("✅ Security headers configured")
        print("✅ Health check endpoints added")
        
    except Exception as e:
        print(f"⚠️ Monitoring initialization error: {e}")

# Load configuration from environment
try:
    if CONFIG_LOADED:
        app.config.from_object(current_config)
        current_config.validate_required_config()
        print("✅ Environment variables validated")
        db_config = current_config.get_database_config()
        ai_config = current_config.get_ai_config()
    else:
        # Use fallback configuration
        db_config = {'type': 'supabase'}
        ai_config = {'enabled': True}
    
    app.secret_key = current_config.SECRET_KEY
    print(f"✅ Flask configured for {current_config.FLASK_ENV} environment")
    
except Exception as e:
    print(f"⚠️ Configuration error: {e}")
    # Final fallback configuration
    app.secret_key = 'real-estate-crm-secret-key-2025'
    db_config = {'type': 'sqlite', 'path': 'real_estate_crm.db'}
    ai_config = {'enabled': False}

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'real_estate_crm.db')

# Gemini API Configuration from environment
GEMINI_API_KEY = getattr(current_config, 'GEMINI_API_KEY', None) or os.environ.get('GEMINI_API_KEY', 'your-gemini-api-key-here')

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

# ============================================================================
# DATA VALIDATION SYSTEM (Task #4)
# ============================================================================

import re
from typing import Dict, Any, List, Tuple

def validate_extracted_data(data: Dict[str, Any], operation_type: str) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Validate extracted data before database operations.
    
    Args:
        data: Extracted data dictionary
        operation_type: Type of operation (create_client, create_property, etc.)
        
    Returns:
        Tuple of (is_valid, error_messages, cleaned_data)
    """
    errors = []
    cleaned_data = {}
    
    if operation_type == 'create_client':
        # Required fields
        if not data.get('first_name') or not data.get('last_name'):
            errors.append("First name and last name are required")
        else:
            cleaned_data['first_name'] = str(data['first_name']).strip().title()
            cleaned_data['last_name'] = str(data['last_name']).strip().title()
        
        # Email validation
        if data.get('email'):
            email = str(data['email']).strip().lower()
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                errors.append("Invalid email format")
            else:
                cleaned_data['email'] = email
        
        # Phone validation
        if data.get('phone'):
            phone = str(data['phone']).strip()
            # Remove all non-digits
            phone_digits = re.sub(r'\D', '', phone)
            if len(phone_digits) not in [10, 11]:
                errors.append("Phone number must be 10 or 11 digits")
            else:
                # Format as (XXX) XXX-XXXX
                if len(phone_digits) == 11 and phone_digits[0] == '1':
                    phone_digits = phone_digits[1:]
                cleaned_data['phone'] = f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
        
        # Client type validation
        if data.get('client_type'):
            client_type = str(data['client_type']).lower().strip()
            if client_type not in ['buyer', 'seller', 'both']:
                cleaned_data['client_type'] = 'buyer'  # Default
            else:
                cleaned_data['client_type'] = client_type
        else:
            cleaned_data['client_type'] = 'buyer'  # Default
            
    elif operation_type == 'create_property':
        # Required fields for properties
        required_fields = ['address_line1', 'city', 'state', 'zip_code']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"{field.replace('_', ' ').title()} is required")
            else:
                cleaned_data[field] = str(data[field]).strip()
        
        # Price validation
        if data.get('listing_price'):
            try:
                price = float(str(data['listing_price']).replace('$', '').replace(',', ''))
                if price <= 0:
                    errors.append("Listing price must be greater than 0")
                else:
                    cleaned_data['listing_price'] = price
            except (ValueError, TypeError):
                errors.append("Invalid listing price format")
        
        # Numeric field validation
        numeric_fields = ['bedrooms', 'bathrooms', 'square_feet']
        for field in numeric_fields:
            if data.get(field):
                try:
                    value = float(data[field])
                    if value < 0:
                        errors.append(f"{field.replace('_', ' ').title()} cannot be negative")
                    else:
                        cleaned_data[field] = value
                except (ValueError, TypeError):
                    errors.append(f"Invalid {field.replace('_', ' ')} format")
    
    # Copy remaining safe fields
    safe_fields = ['address_street', 'address_city', 'address_state', 'occupation', 'property_type']
    for field in safe_fields:
        if data.get(field):
            cleaned_data[field] = str(data[field]).strip()
    
    is_valid = len(errors) == 0
    return is_valid, errors, cleaned_data

def format_validation_errors(errors: List[str]) -> str:
    """Format validation errors for user display"""
    if not errors:
        return ""
    
    if len(errors) == 1:
        return f"⚠️ {errors[0]}"
    
    error_list = "\n".join([f"• {error}" for error in errors])
    return f"⚠️ Please fix the following issues:\n{error_list}"

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
        from database.streamlined_zipform_functions import STREAMLINED_ZIPFORM_FUNCTIONS
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

def create_langchain_tools():
    """
    Create LangChain tools from our AI_CALLABLE_FUNCTIONS for function calling
    
    Returns:
        list: LangChain Tool objects for Gemini function calling
    """
    from langchain_core.tools import Tool
    
    # Import our CRM functions - use local functions, not zipform imports
    if ZIPFORM_AVAILABLE:
        from zipform_ai_functions import (
            create_client_zipform, create_property_zipform, create_transaction
        )
    
    # Note: find_clients, update_client, create_client are defined locally in this file
    
    tools = []
    
    # Create Client Tool
    def create_client_tool(first_name: str, last_name: str, email: str = None, 
                          phone: str = None, client_type: str = "buyer", 
                          budget_min: int = None, budget_max: int = None,
                          area_preference: str = None, bedrooms: int = None,
                          **kwargs) -> str:
        """Create a new client record in the CRM"""
        if ZIPFORM_AVAILABLE:
            result = create_client_zipform(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                client_type=client_type,
                budget_min=budget_min,
                budget_max=budget_max,
                area_preference=area_preference,
                bedrooms=bedrooms,
                **kwargs
            )
            return f"Client creation result: {result['message']}"
        else:
            # Use local create_client function as fallback
            result = create_client(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                client_type=client_type,
                budget_min=budget_min,
                budget_max=budget_max,
                area_preference=area_preference,
                bedrooms=bedrooms,
                **kwargs
            )
            return f"Client creation result: {result['message']}"
    
    tools.append(Tool(
        name="create_client",
        description="""Create a new client record in the CRM. Use when user mentions adding a new person to the database.
        Parameters:
        - first_name (required): Client's first name
        - last_name (required): Client's last name  
        - email (optional): Email address
        - phone (optional): Phone number (normalize 9-digit to 10-digit if possible)
        - client_type (optional): 'buyer', 'seller', or 'both' (default: buyer)
        - budget_min (optional): Minimum budget as integer (e.g., 500000 for $500K)
        - budget_max (optional): Maximum budget as integer  
        - area_preference (optional): Preferred area/neighborhood
        - bedrooms (optional): Number of bedrooms needed
        Example: "add jennifer lawrence to the crm she wants to buy a house for 799999 dollars in penn valley and can be contacted at 747567574"
        """,
        func=create_client_tool
    ))
    
    # Find Clients Tool
    def find_clients_tool(search_term: str = None, first_name: str = None, 
                         last_name: str = None, email: str = None, 
                         phone: str = None) -> str:
        """Search for existing clients in the CRM"""
        result = find_clients(
            search_term=search_term,
            client_type=None,
            limit=10
        )
        if result.get('success'):
            return f"Found {result.get('count', 0)} clients: {result.get('message', 'No details')}"
        else:
            return f"Search failed: {result.get('message', 'Unknown error')}"
    
    tools.append(Tool(
        name="find_clients",
        description="""Search for existing clients in the CRM database.
        Parameters:
        - search_term (optional): General search across name, email, phone
        - first_name (optional): Search by first name
        - last_name (optional): Search by last name
        - email (optional): Search by email address
        - phone (optional): Search by phone number
        Use when user asks to find, search, or look up existing clients.
        """,
        func=find_clients_tool
    ))
    
    # Update Client Tool
    def update_client_tool(client_id: int, **kwargs) -> str:
        """Update an existing client's information"""
        result = update_client(client_id=client_id, **kwargs)
        return f"Client update result: {result['message']}"
    
    tools.append(Tool(
        name="update_client",
        description="""Update an existing client's information in the CRM.
        Parameters:
        - client_id (required): The ID of the client to update
        - first_name (optional): New first name
        - last_name (optional): New last name
        - email (optional): New email address
        - phone (optional): New phone number
        - client_type (optional): buyer, seller, or both
        - budget_min (optional): Minimum budget as integer
        - budget_max (optional): Maximum budget as integer
        - area_preference (optional): Preferred area/neighborhood
        Use when user wants to modify existing client information.
        """,
        func=update_client_tool
    ))
    
    # Create Property Tool
    def create_property_tool(address_line1: str, city: str, state: str, 
                           zip_code: str, **kwargs) -> str:
        """Create a new property listing"""
        if ZIPFORM_AVAILABLE:
            result = create_property_zipform(
                street_address=address_line1,
                city=city,
                state=state,
                zip_code=zip_code,
                **kwargs
            )
            return f"Property creation result: {result['message']}"
        else:
            return "ZipForm functions not available"
    
    tools.append(Tool(
        name="create_property",
        description="""Create a new property listing in the CRM.
        Parameters:
        - address_line1 (required): Street address
        - city (required): City name
        - state (required): State code (e.g., CA)
        - zip_code (required): ZIP code
        - listed_price (optional): Listing price as integer
        - bedrooms (optional): Number of bedrooms
        - bathrooms (optional): Number of bathrooms
        - square_feet (optional): Square footage
        - property_type (optional): single_family, condo, townhouse, etc.
        - mls_number (optional): MLS listing number
        Use when user wants to add a new property to the system.
        """,
        func=create_property_tool
    ))
    
    # Find Properties Tool
    def find_properties_tool(search_term: str = None, min_price: int = None,
                           max_price: int = None, bedrooms: int = None,
                           city: str = None, limit: int = 10) -> str:
        """Search for properties in the CRM"""
        result = find_properties(
            search_term=search_term,
            min_price=min_price,
            max_price=max_price,
            bedrooms=bedrooms,
            city=city,
            limit=limit
        )
        return f"Found {result.get('count', 0)} properties: {result.get('message', 'No details')}"
    
    tools.append(Tool(
        name="find_properties",
        description="""Search for properties in the CRM database.
        Parameters:
        - search_term (optional): Search in address or MLS number
        - min_price (optional): Minimum listing price
        - max_price (optional): Maximum listing price
        - bedrooms (optional): Number of bedrooms
        - city (optional): City filter
        - limit (optional): Maximum results (default: 10)
        Use when user wants to search for properties by criteria.
        """,
        func=find_properties_tool
    ))
    
    # Create Transaction Tool
    def create_transaction_tool(transaction_type: str, property_id: int,
                              buyer_client_id: int = None, seller_client_id: int = None,
                              **kwargs) -> str:
        """Create a new transaction"""
        if ZIPFORM_AVAILABLE:
            result = create_transaction(
                transaction_type=transaction_type,
                property_id=property_id,
                buyer_client_id=buyer_client_id,
                seller_client_id=seller_client_id,
                **kwargs
            )
            return f"Transaction creation result: {result['message']}"
        else:
            return "ZipForm functions not available"
    
    tools.append(Tool(
        name="create_transaction",
        description="""Create a new transaction in the CRM.
        Parameters:
        - transaction_type (required): purchase, sale, or lease
        - property_id (required): Property ID for the transaction
        - buyer_client_id (optional): Buyer client ID
        - seller_client_id (optional): Seller client ID
        - purchase_price (optional): Purchase price as integer
        - offer_date (optional): Offer date (YYYY-MM-DD format)
        - closing_date (optional): Expected closing date
        - earnest_money_amount (optional): Earnest money deposit
        Use when user wants to create a new real estate transaction.
        """,
        func=create_transaction_tool
    ))
    
    return tools

def build_function_calling_context():
    """
    Build system prompt specifically for function calling approach
    
    Returns:
        str: Enhanced system prompt for Gemini function calling
    """
    return """You are an intelligent Real Estate CRM Assistant for Narissa Realty. You have direct access to CRM database functions through function calling.

🧠 CORE BEHAVIOR:
1. **UNDERSTAND** what the user wants to do with their CRM data
2. **ANALYZE** the message for client information (names, phones, emails, budgets, preferences)
3. **CALL FUNCTIONS** directly when you identify CRM operations needed
4. **EXTRACT CAREFULLY** - Handle edge cases with precision

🎯 COMPREHENSIVE FEW-SHOT EXAMPLES:

**EXAMPLE 1 - Complex Client Creation:**
Input: "add jennifer lawrence to the crm she wants to buy a house for 79999999 dollars in penn valley and can be contacted at 747567574"
→ Call create_client(
    first_name="Jennifer",
    last_name="Lawrence", 
    client_type="buyer",
    budget_min=79999999,
    area_preference="Penn Valley",
    phone="(747) 567-574"  # Formatted 9-digit with area code assumption
)

**EXAMPLE 2 - Email and Phone Combination:**
Input: "Create contact: Sarah Johnson, looking to sell, email sarah.j@gmail.com, phone (555) 123-4567"
→ Call create_client(
    first_name="Sarah",
    last_name="Johnson",
    client_type="seller",
    email="sarah.j@gmail.com",
    phone="(555) 123-4567"
)

**EXAMPLE 3 - Budget Formats:**
Input: "Add client Mike Chen, buyer, budget 750K to 1.2M, phone 4155551234"
→ Call create_client(
    first_name="Mike",
    last_name="Chen",
    client_type="buyer", 
    budget_min=750000,
    budget_max=1200000,
    phone="(415) 555-1234"
)

**EXAMPLE 4 - Search Variations:**
Input: "find john smith in the database"
→ Call find_clients(search_term="John Smith")

Input: "show me all buyers"
→ Call find_clients(client_type="buyer")

**EXAMPLE 5 - Property Creation:**
Input: "Add property: 123 Main St, Sacramento CA 95814, 3br 2ba, $500,000"
→ Call create_property(
    address_line1="123 Main St",
    city="Sacramento", 
    state="CA",
    zip_code="95814",
    bedrooms=3,
    bathrooms=2,
    listing_price=500000
)

**EXAMPLE 6 - Edge Cases:**
Input: "client emma watson, 9876543210, wants house"
→ Call create_client(
    first_name="Emma",
    last_name="Watson",
    client_type="buyer",
    phone="(987) 654-3210"  # 10-digit number formatted
)

🔍 ENHANCED EXTRACTION RULES:
- **Names**: Always Title Case (emma watson → Emma Watson)
- **Phones**: 
  - 10 digits: (XXX) XXX-XXXX
  - 9 digits: Add area code based on context, format as (XXX) XXX-XXXX
  - 7 digits: Assume local, add default area code
- **Budgets**: 
  - "500K" → 500000
  - "1.5M" → 1500000  
  - "750,000" → 750000
  - "750000 dollars" → 750000
- **Areas**: Title Case (penn valley → Penn Valley)
- **Client Type**: 
  - "wants to buy", "looking to purchase", "buyer" → "buyer"
  - "selling", "wants to sell", "seller" → "seller"
- **Emails**: Always lowercase normalization

🚨 VALIDATION & SAFETY:
- Always validate extracted data before function calls
- Provide clear conversational response explaining what you did
- For ambiguous input, ask clarifying questions
- Handle errors gracefully with specific guidance

🎯 RESPONSE STYLE:
- Be concise and professional
- Confirm what data was extracted
- Explain any assumptions made (e.g., area code additions)
- Always respond conversationally after function calls

Use these examples as your training foundation for consistent, accurate extraction."""

def get_gemini_response_with_function_calling(message, context="", conversation_history=None):
    """
    Enhanced AI response using Gemini Function Calling for direct CRM operations
    
    Args:
        message (str): User message
        context (str): Additional context (optional)
        conversation_history (list): Previous messages for context
    
    Returns:
        dict: {'response': str, 'function_calls': list, 'confidence': float}
    """
    if not GEMINI_CONFIGURED:
        return {
            'response': "AI service is currently unavailable. Please check configuration.",
            'function_calls': [],
            'confidence': 0.0
        }
    
    try:
        # Use LangChain approach with function calling
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_core.tools import Tool
        
        llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash-preview-04-17",
            google_api_key=GEMINI_API_KEY,
            temperature=0.1
        )
        
        # Define CRM functions as LangChain tools for function calling
        tools = create_langchain_tools()
        
        # Create function-calling enabled LLM
        llm_with_tools = llm.bind_tools(tools)
        
        # Build enhanced system prompt for function calling
        system_prompt = build_function_calling_context()
        
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
                    from langchain_core.messages import AIMessage
                    messages.append(AIMessage(content=hist_msg['content']))
        
        # Add current user message
        messages.append(HumanMessage(content=message))
        
        # Get response with function calling
        response = llm_with_tools.invoke(messages)
        
        # Parse function calls and response
        function_calls = []
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Check if response includes tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                function_calls.append({
                    'function': tool_call['name'],
                    'parameters': tool_call['args'],
                    'reason': 'AI function calling',
                    'confidence': 0.95
                })
        
        return {
            'response': response_text,
            'function_calls': function_calls,
            'confidence': 0.9 if function_calls else 0.7
        }
        
    except Exception as e:
        print(f"[GEMINI FUNCTION CALLING ERROR] {str(e)}")
        return {
            'response': f"I apologize, but I'm experiencing technical difficulties with function calling. Please try again later. (Error: {str(e)[:50]}...)",
            'function_calls': [],
            'confidence': 0.0
        }

def get_gemini_response(message, context="", conversation_history=None):
    """
    Legacy AI response function - now redirects to function calling approach
    
    Args:
        message (str): User message
        context (str): Additional context (optional)
        conversation_history (list): Previous messages for context
    
    Returns:
        dict: {'response': str, 'suggested_functions': list, 'confidence': float}
    """
    # Use new function calling approach
    result = get_gemini_response_with_function_calling(message, context, conversation_history)
    
    # Convert function_calls to suggested_functions for backward compatibility
    suggested_functions = []
    for fc in result.get('function_calls', []):
        suggested_functions.append({
            'function': fc['function'],
            'parameters': fc['parameters'],
            'reason': fc['reason'],
            'confidence': fc['confidence']
        })
    
    return {
        'response': result['response'],
        'suggested_functions': suggested_functions,
        'confidence': result['confidence']
    }

# REMOVED: analyze_response_for_functions() - replaced with direct LangChain function calling
# This function used brittle regex patterns to detect AI proposals
# Now using structured function calling results from get_gemini_response_with_function_calling()

def extract_entities_from_text(text):
    """
    AI-native entity extraction with legacy regex fallback
    
    Args:
        text (str): Text to analyze for entity extraction
        
    Returns:
        dict: Extracted entity data
    """
    try:
        # Try AI-native extraction first using function calling
        if GEMINI_CONFIGURED:
            result = get_gemini_response_with_function_calling(
                message=f"Extract client information from: {text}",
                context="Extract structured client data including first_name, last_name, phone, email, budget information."
            )
            
            # If AI found function calls, extract entities from the parameters
            if result.get('function_calls'):
                for fc in result['function_calls']:
                    if fc['function'] == 'create_client' and fc.get('parameters'):
                        # Parse the parameters and return as entities dict
                        params = fc['parameters']
                        entities = {}
                        
                        # Handle different parameter formats
                        if isinstance(params, dict):
                            # Direct parameter dictionary
                            for key, value in params.items():
                                if key in ['first_name', 'last_name', 'phone', 'email', 'budget_min', 'budget_max']:
                                    entities[key] = value
                        elif isinstance(params, str):
                            # Parse string format like 'first_name="Jennifer", last_name="Lawrence"'
                            import re
                            for match in re.finditer(r'(\w+)="([^"]*)"', params):
                                key, value = match.groups()
                                if key in ['first_name', 'last_name', 'phone', 'email', 'budget_min', 'budget_max']:
                                    entities[key] = value
                        
                        if entities:
                            print(f"[AI EXTRACTION] Successfully extracted {len(entities)} entities using AI")
                            return entities
    
    except Exception as e:
        print(f"[AI EXTRACTION ERROR] {str(e)}, falling back to legacy regex")
    
    # Fallback to legacy regex extraction
    print(f"[FALLBACK] Using legacy regex extraction for: {text[:50]}...")
    return extract_entities_from_text_legacy(text)

def extract_entities_from_text_legacy(text):
    """
    Extract CRM entities from text using regex patterns
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Extracted entity data
    """
    import re
    
    entities = {}
    
    # Name patterns - enhanced to catch more formats (case insensitive)
    name_patterns = [
        r"(?:client record for|add|create client)\s+([a-z]+\s+[a-z]+)",
        r"Name:\s*([a-z]+\s+[a-z]+)",
        r"([a-z]+\s+[a-z]+)(?:'s record|\s+called|\s+at the)",
        r"^([a-z]+\s+[a-z]+),",  # "jessica martinez," at start of line
        r"([a-z]+\s+[a-z]+)\s+called",  # "john smith called"
        r"add\s+([a-z]+\s+[a-z]+)\s+to",  # "add jennifer lawrence to"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            full_name = match.group(1).strip()
            name_parts = full_name.split()
            if len(name_parts) >= 2:
                entities['first_name'] = name_parts[0]
                entities['last_name'] = ' '.join(name_parts[1:])
            break
    
    # Phone patterns - enhanced to catch more formats
    phone_patterns = [
        r"(?:phone|cell|number)[:\s]*([\\(]?\d{3}[\\)]?[\s.-]?\d{3}[\s.-]?\d{4})",  # phone: 555-123-4567
        r"(?:his|her|my)\s+phone\s+(?:is\s+|number\s+is\s+)?([\\(]?\d{3}[\\)]?[\s.-]?\d{3}[\s.-]?\d{4})",  # his phone is 555-123-4567
        r"([\\(]?\d{3}[\\)]?[\s.-]?\d{3}[\s.-]?\d{4})",  # standalone phone number anywhere
        r"(\d{10})",  # 10 digit number without separators
    ]
    
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text, re.IGNORECASE)
        if phone_match:
            entities['phone'] = phone_match.group(1)
            break
    
    # Email patterns - enhanced to catch more formats
    email_patterns = [
        r"(?:email|e-mail)[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",  # email: user@domain.com
        r"(?:his|her|my)\s+email\s+(?:is\s+|address\s+is\s+)?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",  # his email is user@domain.com
        r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",  # standalone email anywhere
    ]
    
    for pattern in email_patterns:
        email_match = re.search(pattern, text, re.IGNORECASE)
        if email_match:
            entities['email'] = email_match.group(1)
            break
    
    # Budget/price patterns - enhanced to catch more formats
    budget_patterns = [
        r"(?:budget|under|up to)[:\s]*\$?([\d,]+)K?",  # budget: $500K
        r"(?:with a budget of|budget is|can spend)[:\s]*\$?([\d,]+)K?",  # with a budget of $450000
        r"(?:for)\s+\$?([\d,]{4,})(?![-.\d])",  # for $76000 (must be 4+ digits to avoid phone numbers)
        r"\$+([\d,]{4,})(?![-.\d])",  # standalone large numbers like $450000 (with $ sign)
    ]
    
    for pattern in budget_patterns:
        budget_match = re.search(pattern, text, re.IGNORECASE)
        if budget_match:
            budget_str = budget_match.group(1).replace(',', '')
            if 'K' in budget_match.group(0).upper():
                entities['budget'] = int(budget_str) * 1000
            else:
                entities['budget'] = int(budget_str)
            break
    
    # Area/location preferences - enhanced patterns
    area_patterns = [
        r"(?:in|looking in|area preference)[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s+for|\s+with|\s*$)",  # in Sacramento
        r"(?:house|property|home)\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s+for|\s+with|\s*$)",  # house in Nevada County
        r"([A-Z][a-z]+\s+County)(?!\s+[a-z])",  # Nevada County
        r"(?:Location|Area)[:]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",  # Location: Sacramento
    ]
    
    for pattern in area_patterns:
        area_match = re.search(pattern, text, re.IGNORECASE)
        if area_match:
            entities['area_preference'] = area_match.group(1).strip()
            break
    
    # Bedrooms - enhanced patterns  
    bedroom_patterns = [
        r"(\d+)\s*(?:bedroom|br|bed)",  # 3 bedroom
        r"(?:bedroom|br|bed)[:\s]*(\d+)",  # bedroom: 3
        r"(\d+)BR",  # 3BR
    ]
    
    for pattern in bedroom_patterns:
        bedroom_match = re.search(pattern, text, re.IGNORECASE)
        if bedroom_match:
            entities['bedrooms'] = int(bedroom_match.group(1))
            break
    
    # Client type inference
    if any(word in text.lower() for word in ['looking for', 'buyer', 'buying', 'purchase']):
        entities['client_type'] = 'buyer'
    elif any(word in text.lower() for word in ['selling', 'seller', 'list', 'listing']):
        entities['client_type'] = 'seller'
    else:
        entities['client_type'] = 'buyer'  # Default
    
    print(f"[DEBUG ENTITY EXTRACTION] Input text: {text}")
    print(f"[DEBUG ENTITY EXTRACTION] Extracted entities: {entities}")
    
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
        with open('database/real_estate_crm_schema.sql', 'r') as f:
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
    AI_CALLABLE_FUNCTIONS.update(STREAMLINED_ZIPFORM_FUNCTIONS)
    print("✅ ZipForm AI functions integrated with chatbot")
else:
    print("⚠️  Running with legacy functions only")

# Add Offer Creation functions if available
if OFFER_CREATION_AVAILABLE:
    AI_CALLABLE_FUNCTIONS.update(OFFER_CREATION_AI_FUNCTIONS)
    print("✅ Offer Creation AI functions integrated with chatbot")
else:
    print("⚠️  Running without offer creation capabilities")

@app.route('/')
def dashboard():
    """Main dashboard view"""
    # Get dashboard statistics using new database configuration
    try:
        client_stats = db.get_clients_summary()
        
        # Get other statistics
        total_transactions = db.execute_query('SELECT COUNT(*) as count FROM transactions', fetch_one=True)
        total_properties = db.execute_query('SELECT COUNT(*) as count FROM properties', fetch_one=True)
        
        stats = {
            'total_clients': client_stats.get('total_clients', 0),
            'active_transactions': total_transactions[0] if total_transactions else 0,
            'properties': total_properties[0] if total_properties else 0,
            'this_month_closings': 0  # Simplified for now
        }
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        stats = {
            'total_clients': 0,
            'active_transactions': 0,
            'properties': 0,
            'this_month_closings': 0
        }
    
    # Get recent transactions using new database configuration
    try:
        recent_transactions = db.execute_query('''
            SELECT t.id, t.status, t.purchase_price, t.offer_date, 
                   'Address TBD' as address_street, 'City TBD' as address_city,
                   'Buyer TBD' as buyer_first, '' as buyer_last,
                   'Seller TBD' as seller_first, '' as seller_last
            FROM transactions t
            ORDER BY t.created_at DESC
            LIMIT 10
        ''', fetch_all=True)
    except Exception as e:
        print(f"Error getting recent transactions: {e}")
        recent_transactions = []
    
    return render_template('crm_dashboard.html', stats=stats, recent_transactions=recent_transactions)

@app.route('/debug_chat')
def debug_chat():
    """Debug chat interface for testing chatbot functionality"""
    return render_template('debug_chat.html')

@app.route('/clients')
def clients_list():
    """View all clients"""
    if CONFIG_LOADED and current_config.USE_SUPABASE:
        # Use Supabase API via database config
        clients = db.get_all_clients()
    else:
        # Fallback to SQLite
        conn = get_db_connection()
        clients = conn.execute('''
            SELECT id, client_type, first_name, last_name, email, home_phone, 
                   city, created_at
            FROM clients 
            ORDER BY last_name, first_name
        ''').fetchall()
        conn.close()
        clients = [dict(row) for row in clients]
    return render_template('clients_list.html', clients=clients)

@app.route('/clients/new', methods=['GET', 'POST'])
def new_client():
    """Add new client"""
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO clients (
                client_type, first_name, last_name, email, home_phone, city, 
                budget_min, budget_max, area_preference, bedrooms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('client_type', 'Buyer'), 
            data.get('first_name', ''), 
            data.get('last_name', ''), 
            data.get('email'),
            data.get('home_phone'), 
            data.get('city'),
            data.get('budget_min') or None,
            data.get('budget_max') or None,
            data.get('area_preference'),
            data.get('bedrooms') or None
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
    if CONFIG_LOADED and current_config.USE_SUPABASE:
        # Use Supabase API via database config
        properties = db.get_all_properties()
        # For now, return all properties without filtering (can add filtering later)
        cities = []  # Can implement city filtering in database_config.py later
    else:
        # Fallback to SQLite
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
        properties = [dict(row) for row in properties]
        
        # Get unique cities for dropdown
        cities = conn.execute('SELECT DISTINCT city FROM properties WHERE city IS NOT NULL ORDER BY city').fetchall()
        cities = [dict(row) for row in cities]
        
        conn.close()
    
    return render_template('properties_list.html', 
                         properties=properties, 
                         cities=cities,
                         search=request.args.get('search', ''),
                         property_type=request.args.get('property_type', ''),
                         city=request.args.get('city', ''))

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
                # TASK #4: VALIDATE EXTRACTED DATA BEFORE PROPOSING OPERATION
                is_valid, validation_errors, cleaned_data = validate_extracted_data(
                    suggestion['parameters'], 
                    suggestion['function']
                )
                
                if not is_valid:
                    # Send validation errors back to user immediately
                    print(f"[VALIDATION ERROR] {suggestion['function']}: {validation_errors}")
                    return jsonify({
                        'response': f"I found some issues with the information provided:\n\n{format_validation_errors(validation_errors)}\n\nPlease provide the correct information and I'll help you create the record.",
                        'validation_errors': validation_errors,
                        'error_type': 'validation',
                        'timestamp': datetime.now().isoformat()
                    })
                
                # AI proposed a database operation with validated data
                operation_id = f"op_{int(datetime.now().timestamp())}_{suggestion['function']}"
                
                # Store the proposed operation for user confirmation (using cleaned data)
                pending_operations[operation_id] = {
                    'operation_type': suggestion['function'],
                    'operation_data': cleaned_data,  # Use validated/cleaned data
                    'context': 'AI Smart Analysis',
                    'user_message': user_message,
                    'ai_response': ai_result['response'],
                    'status': 'pending_confirmation',
                    'created_at': datetime.now().isoformat(),
                    'ai_confidence': suggestion.get('confidence', 0),
                    'proposal_text': suggestion.get('proposal_text', ''),
                    'validation_passed': True
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
        
        # GUARANTEED ENTITY EXTRACTION: Always try to extract entities from user input
        # This ensures we capture data even if AI response patterns fail
        guaranteed_entities = extract_entities_from_text(user_message)
        
        # If we have good entity extraction but no smart proposals, create a guaranteed proposal
        if guaranteed_entities and len(guaranteed_entities) >= 2 and not proposed_operations:
            operation_type = 'create_client'  # Default to client creation
            
            # TASK #4: VALIDATE GUARANTEED ENTITIES
            is_valid, validation_errors, cleaned_data = validate_extracted_data(
                guaranteed_entities, 
                operation_type
            )
            
            if not is_valid:
                # Send validation errors back to user
                print(f"[VALIDATION ERROR] Guaranteed {operation_type}: {validation_errors}")
                return jsonify({
                    'response': f"I extracted some information but found issues:\n\n{format_validation_errors(validation_errors)}\n\nPlease provide the correct information and I'll help you create the record.",
                    'validation_errors': validation_errors,
                    'error_type': 'validation',
                    'timestamp': datetime.now().isoformat()
                })
            
            operation_id = f"op_{int(datetime.now().timestamp())}_guaranteed_{operation_type}"
            
            pending_operations[operation_id] = {
                'operation_type': operation_type,
                'operation_data': cleaned_data,  # Use validated data
                'context': 'Guaranteed Entity Extraction',
                'user_message': user_message,
                'status': 'pending_confirmation',
                'created_at': datetime.now().isoformat(),
                'ai_confidence': ai_result.get('confidence', 0),
                'validation_passed': True
            }
            
            proposed_operations.append({
                'operation_id': operation_id,
                'type': operation_type,
                'data': cleaned_data,  # Use validated data
                'confidence': ai_result.get('confidence', 0),
                'formatted_preview': format_operation_for_review(operation_type, cleaned_data)
            })
            
            print(f"[GUARANTEED PROPOSAL] {operation_id}: Extracted {len(guaranteed_entities)} entities from user input")
        
        # Fallback: if still no proposals and AI has moderate confidence, try combined text
        elif not proposed_operations and ai_result.get('confidence', 0) >= 0.6:
            fallback_entities = extract_entities_from_text(f"{user_message} {ai_result['response']}")
            if fallback_entities and len(fallback_entities) >= 2:  # At least 2 fields extracted
                operation_type = 'create_client'  # Default to client creation
                
                # TASK #4: VALIDATE FALLBACK ENTITIES
                is_valid, validation_errors, cleaned_data = validate_extracted_data(
                    fallback_entities, 
                    operation_type
                )
                
                if not is_valid:
                    # Send validation errors back to user
                    print(f"[VALIDATION ERROR] Fallback {operation_type}: {validation_errors}")
                    return jsonify({
                        'response': f"I tried to extract information from our conversation but found issues:\n\n{format_validation_errors(validation_errors)}\n\nPlease provide the correct information and I'll help you create the record.",
                        'validation_errors': validation_errors,
                        'error_type': 'validation',
                        'timestamp': datetime.now().isoformat()
                    })
                
                operation_id = f"op_{int(datetime.now().timestamp())}_fallback_{operation_type}"
                
                pending_operations[operation_id] = {
                    'operation_type': operation_type,
                    'operation_data': cleaned_data,  # Use validated data
                    'context': 'Fallback Entity Extraction',
                    'user_message': user_message,
                    'status': 'pending_confirmation',
                    'created_at': datetime.now().isoformat(),
                    'ai_confidence': ai_result.get('confidence', 0),
                    'validation_passed': True
                }
                
                proposed_operations.append({
                    'operation_id': operation_id,
                    'type': operation_type,
                    'data': cleaned_data,  # Use validated data
                    'confidence': ai_result.get('confidence', 0),
                    'formatted_preview': format_operation_for_review(operation_type, cleaned_data)
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
        
    # ============================================================================
    # TASK #5: TIERED ERROR HANDLING AND CLARIFICATION
    # ============================================================================
    except ValueError as e:
        # Data parsing or validation errors
        error_msg = str(e)
        print(f"[VALIDATION ERROR] {error_msg}")
        
        if "email" in error_msg.lower():
            clarification = "Could you please provide a valid email address? For example: john@example.com"
        elif "phone" in error_msg.lower():
            clarification = "Could you please provide a valid phone number? For example: (555) 123-4567 or 555-123-4567"
        elif "name" in error_msg.lower():
            clarification = "Could you please provide both first and last name? For example: 'John Smith'"
        else:
            clarification = "Could you please check the information you provided and try again?"
        
        return jsonify({
            'error': 'validation_error',
            'error_type': 'validation',
            'message': error_msg,
            'response': f"⚠️ {error_msg}\n\n{clarification}",
            'clarification': clarification,
            'timestamp': datetime.now().isoformat()
        }), 400
        
    except ConnectionError as e:
        # AI API connection errors
        print(f"[AI API ERROR] Connection failed: {str(e)}")
        return jsonify({
            'error': 'ai_api_error',
            'error_type': 'connection',
            'message': 'Unable to connect to AI service',
            'response': '🔌 I\'m having trouble connecting to the AI service right now. Please check your internet connection and try again in a moment.',
            'fallback_response': 'AI service temporarily unavailable',
            'timestamp': datetime.now().isoformat()
        }), 503
        
    except KeyError as e:
        # Missing required data fields
        missing_field = str(e).strip("'\"")
        print(f"[DATA ERROR] Missing required field: {missing_field}")
        
        field_suggestions = {
            'message': 'Please include a message in your request',
            'first_name': 'Please provide a first name',
            'last_name': 'Please provide a last name',
            'email': 'Please provide an email address',
            'phone': 'Please provide a phone number'
        }
        
        suggestion = field_suggestions.get(missing_field, f'Please provide the {missing_field} field')
        
        return jsonify({
            'error': 'missing_field',
            'error_type': 'missing_data',
            'message': f'Missing required field: {missing_field}',
            'response': f"📝 {suggestion}. Could you please provide this information so I can help you?",
            'clarification': suggestion,
            'missing_field': missing_field,
            'timestamp': datetime.now().isoformat()
        }), 400
        
    except sqlite3.IntegrityError as e:
        # Database constraint violations (duplicates, etc.)
        error_msg = str(e)
        print(f"[DATABASE ERROR] Integrity constraint: {error_msg}")
        
        if "UNIQUE constraint failed" in error_msg:
            if "email" in error_msg:
                clarification = "A client with this email address already exists. Would you like me to find the existing client or use a different email?"
            elif "phone" in error_msg:
                clarification = "A client with this phone number already exists. Would you like me to find the existing client or use a different phone number?"
            else:
                clarification = "This record already exists in the database. Would you like me to find the existing record instead?"
        else:
            clarification = "There was a database constraint issue. Could you please check your data and try again?"
        
        return jsonify({
            'error': 'database_constraint',
            'error_type': 'database',
            'message': 'Data already exists',
            'response': f"🗃️ {clarification}",
            'clarification': clarification,
            'timestamp': datetime.now().isoformat()
        }), 409
        
    except sqlite3.Error as e:
        # General database errors
        print(f"[DATABASE ERROR] {str(e)}")
        return jsonify({
            'error': 'database_error',
            'error_type': 'database',
            'message': str(e),
            'response': '🗃️ I encountered a database issue. Please try again in a moment. If the problem persists, please contact support.',
            'fallback_response': 'Database temporarily unavailable',
            'timestamp': datetime.now().isoformat()
        }), 500
        
    except Exception as e:
        # Catch-all for unexpected errors
        error_msg = str(e)
        print(f"[UNEXPECTED ERROR] {error_msg}")
        print(f"[UNEXPECTED ERROR] Error type: {type(e).__name__}")
        
        # Try to provide helpful clarification based on error content
        if "timeout" in error_msg.lower():
            clarification = "The request took too long to process. Please try again with a simpler request."
        elif "memory" in error_msg.lower():
            clarification = "The system is running low on resources. Please try again in a moment."
        elif "network" in error_msg.lower():
            clarification = "There seems to be a network issue. Please check your connection and try again."
        else:
            clarification = "An unexpected error occurred. Please try rephrasing your request or contact support if this continues."
        
        return jsonify({
            'error': 'unexpected_error',
            'error_type': 'system',
            'message': error_msg,
            'response': f'⚠️ {clarification}',
            'clarification': clarification,
            'fallback_response': 'I apologize, but I encountered an unexpected issue. Please try again.',
            'timestamp': datetime.now().isoformat()
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

# ============================================================================
# FORM API ENDPOINTS (Integration from form_api_backend.py)
# ============================================================================

@app.route('/api/forms/list', methods=['GET'])
def api_list_forms():
    """Get list of available forms"""
    try:
        print(f"🔍 API call received: /api/forms/list")
        # Return the forms we support
        forms = [
            {
                'id': 'california_purchase_agreement',
                'name': 'California Residential Purchase Agreement',
                'description': 'Standard CAR form for residential property purchases',
                'pages': 12,
                'category': 'purchase',
                'estimated_time': '5-10 minutes',
                'required_data': ['client', 'property']
            },
            {
                'id': 'buyer_representation_agreement', 
                'name': 'Buyer Representation Agreement',
                'description': 'Agreement between buyer and real estate agent',
                'pages': 6,
                'category': 'representation',
                'estimated_time': '3-5 minutes',
                'required_data': ['client']
            },
            {
                'id': 'listing_agreement',
                'name': 'Residential Listing Agreement',
                'description': 'Agreement to list property for sale',
                'pages': 8,
                'category': 'listing',
                'estimated_time': '5-8 minutes', 
                'required_data': ['client', 'property']
            }
        ]
        
        return jsonify({
            'success': True,
            'forms': forms,
            'total_count': len(forms),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/forms/populate', methods=['POST'])
def api_populate_form():
    """Populate a form with CRM data using the real form population system"""
    try:
        data = request.get_json()
        form_id = data.get('form_id')
        client_id = data.get('client_id') 
        property_id = data.get('property_id')
        transaction_id = data.get('transaction_id')
        
        # Import the gorgeous CRPA system
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from crpa_crm_system import CRPACRMSystem
        
        # Initialize CRPA system
        crpa_system = CRPACRMSystem()
        
        # Use transaction_id if provided
        if transaction_id:
            # Create gorgeous CRPA form with real CRM data
            output_filename = f'CRPA_Transaction_{transaction_id}.pdf'
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, output_filename)
            
            result = crpa_system.create_crpa_form(transaction_id, output_path)
        else:
            return jsonify({'success': False, 'error': 'transaction_id is required for CRPA system'}), 400
        
        if result and os.path.exists(output_path):
            return jsonify({
                'success': True,
                'message': f'Gorgeous CRPA form created for transaction {transaction_id} using clean template',
                'pdf_url': f'/download/{output_filename}',
                'pdf_path': output_path,
                'form_type': 'gorgeous_crpa',
                'file_size': os.path.getsize(output_path),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'success': False, 'error': 'Form generation failed'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated PDF files"""
    try:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
        file_path = os.path.join(output_dir, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions')
def api_transactions():
    """Get transactions for dropdown (fix for empty transaction dropdown)"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT t.id, t.purchase_price, t.status, p.street_address as property_address, p.city as property_city
        FROM transactions t 
        LEFT JOIN properties p ON t.property_id = p.id
        ORDER BY t.created_at DESC 
        LIMIT 50
        """)
        
        transactions = []
        for row in cursor.fetchall():
            address = row['property_address'] or 'Unknown Address'
            price = row['purchase_price'] or 0
            transactions.append({
                'id': row['id'],
                'name': f"{address} - ${price:,}" if price > 0 else address,
                'address': address,
                'city': row['property_city'] or 'Unknown City',
                'price': price,
                'status': row['status'] or 'Unknown'
            })
        
        conn.close()
        
        # If no transactions, provide mock data
        if not transactions:
            transactions = [
                {
                    'id': 'trans_001',
                    'name': '456 Oak Avenue - $450,000',
                    'address': '456 Oak Avenue',
                    'city': 'San Francisco',
                    'price': 450000,
                    'status': 'Pending'
                }
            ]
        
        return jsonify({
            'success': True,
            'transactions': transactions
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def init_basic_database():
    """Initialize database schema using the enhanced database configuration"""
    try:
        # Use the global database configuration
        success = db.init_database_schema()
        if success:
            if db.use_supabase:
                print("✅ Supabase PostgreSQL database ready (177-field schema)")
            else:
                print("✅ SQLite database initialized for local development")
        else:
            print("⚠️ Database initialization failed, check configuration")
        return success
        
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")
        return False

if __name__ == '__main__':
    print("🏠 Starting Real Estate CRM Application...")
    
    # Load configuration and validate
    try:
        from config import current_config
        app.config.from_object(current_config)
        current_config.validate_required_config()
        print("✅ Environment variables validated")
    except Exception as e:
        print(f"⚠️ Configuration error: {e}")
    
    # Get server configuration from environment with DigitalOcean compatibility
    host = os.environ.get('HOST', current_config.HOST if 'current_config' in locals() else '0.0.0.0')
    port = int(os.environ.get('PORT', current_config.PORT if 'current_config' in locals() else 5000))
    debug = current_config.DEBUG if 'current_config' in locals() else False
    env = current_config.FLASK_ENV if 'current_config' in locals() else 'development'
    
    # DigitalOcean App Platform uses PORT environment variable
    if os.environ.get('PORT'):
        print(f"🌐 DigitalOcean deployment detected (PORT={port})")
    
    print(f"🌍 Environment: {env}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📡 Host: {host}:{port}")
    print(f"📝 Navigate to: http://localhost:{port}")
    print(f"💻 Dashboard: http://localhost:{port}")
    print(f"👥 Client Management: http://localhost:{port}/clients")
    print(f"🏘️ Property Management: http://localhost:{port}/properties")
    print(f"💼 Transaction Management: http://localhost:{port}/transactions")
    print(f"🤖 AI Chatbot: http://localhost:{port}/debug_chat")
    
    # Initialize database
    init_basic_database()
    
    # Start Flask application
    app.run(debug=debug, host=host, port=port)