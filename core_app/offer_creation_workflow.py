#!/usr/bin/env python3
"""
Offer Creation Workflow Engine
Orchestrates the complete offer creation process from selection to PDF generation
"""

import sqlite3
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
import json
from zipform_ai_functions import get_db_connection

# ============================================================================
# OFFER CREATION WORKFLOW DESIGN
# ============================================================================

class OfferCreationWorkflow:
    """
    Main workflow orchestrator for creating real estate offers
    
    Workflow Steps:
    1. Form Selection - Choose template (CA RPA, etc.)
    2. Entity Selection - Select buyer, property, terms
    3. Data Retrieval - Pull complete data from CRM
    4. Data Validation - Ensure all required fields present
    5. PDF Generation - Create populated offer document
    6. Review & Approval - User confirmation workflow
    7. Transaction Creation - Save offer as transaction record
    """
    
    def __init__(self):
        self.available_forms = {
            'ca_rpa': {
                'name': 'California Residential Purchase Agreement',
                'template_path': 'documents/California_Residential_Purchase_Agreement_FINAL_BLANK.pdf',
                'pages': 27,
                'required_data': [
                    'buyer_info', 'seller_info', 'property_info', 'offer_terms',
                    'financing_info', 'contingencies', 'agent_info', 'disclosures'
                ]
            }
        }
    
    def get_available_forms(self) -> Dict:
        """Return available form templates"""
        return self.available_forms
    
    def start_offer_creation(self, form_type: str, user_request: str) -> Dict:
        """
        Start offer creation workflow from natural language request
        
        Args:
            form_type: Form template to use ('ca_rpa')
            user_request: Natural language description of offer
            
        Returns:
            Dict with workflow state and next steps
        """
        
        # Parse user request for key entities
        parsed_request = self._parse_offer_request(user_request)
        
        # Initialize workflow state
        workflow_state = {
            'form_type': form_type,
            'original_request': user_request,
            'parsed_entities': parsed_request,
            'status': 'entity_selection',
            'required_selections': self._get_required_selections(form_type),
            'collected_data': {},
            'validation_errors': [],
            'workflow_id': f"offer_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        return workflow_state
    
    def _parse_offer_request(self, request: str) -> Dict:
        """
        Parse natural language offer request to extract entities
        
        Expected patterns:
        - "Create offer for 123 Main St with John Smith at $500K"
        - "Generate purchase agreement for [property] with [buyer] offering [price]"
        - "Draft offer for [client] on [address] at [amount] with [terms]"
        """
        
        # This would integrate with existing AI entity extraction
        # For now, return structure for manual testing
        return {
            'property_address': None,
            'buyer_name': None, 
            'offer_price': None,
            'terms': {},
            'confidence': 0.0
        }
    
    def _get_required_selections(self, form_type: str) -> Dict:
        """Get required data selections for form type"""
        
        if form_type == 'ca_rpa':
            return {
                'buyer_client': {
                    'required': True,
                    'type': 'client',
                    'description': 'Primary buyer client'
                },
                'property': {
                    'required': True, 
                    'type': 'property',
                    'description': 'Property to purchase'
                },
                'offer_terms': {
                    'required': True,
                    'type': 'financial',
                    'fields': ['purchase_price', 'down_payment', 'closing_date', 'earnest_money']
                },
                'buyer_agent': {
                    'required': True,
                    'type': 'agent',
                    'description': 'Representing agent'
                },
                'lender': {
                    'required': False,
                    'type': 'lender', 
                    'description': 'Financing lender'
                }
            }
        
        return {}

# ============================================================================
# DATABASE RETRIEVAL FUNCTIONS (MISSING PIECE)
# ============================================================================

def search_clients(search_term: str, limit: int = 10) -> List[Dict]:
    """
    Search clients by name, email, or phone (using actual schema)
    
    Args:
        search_term: Search string to match against client fields
        limit: Maximum results to return
        
    Returns:
        List of matching client records
    """
    try:
        conn = get_db_connection()
        
        query = '''
            SELECT id, first_name, last_name, email, home_phone, 
                   client_type, budget_min, budget_max, area_preference, bedrooms, created_at
            FROM clients 
            WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ? 
               OR home_phone LIKE ?
            ORDER BY last_name, first_name
            LIMIT ?
        '''
        
        search_pattern = f"%{search_term}%"
        results = conn.execute(query, (
            search_pattern, search_pattern, search_pattern,
            search_pattern, limit
        )).fetchall()
        
        clients = []
        for row in results:
            clients.append({
                'id': row['id'],
                'full_name': f"{row['first_name']} {row['last_name']}",
                'email': row['email'],
                'phone': row['home_phone'],
                'client_type': row['client_type'],
                'budget_min': row['budget_min'],
                'budget_max': row['budget_max'],
                'area_preference': row['area_preference'],
                'bedrooms': row['bedrooms'],
                'raw_data': dict(row)
            })
        
        conn.close()
        return clients
        
    except Exception as e:
        print(f"Error searching clients: {e}")
        return []

def search_properties(search_term: str, limit: int = 10) -> List[Dict]:
    """
    Search properties by address, MLS number (using actual schema)
    
    Args:
        search_term: Search string to match against property fields
        limit: Maximum results to return
        
    Returns:
        List of matching property records
    """
    try:
        conn = get_db_connection()
        
        query = '''
            SELECT id, address_line1, city, state, zip_code,
                   mls_number, listing_price, property_type, bedrooms, bathrooms,
                   square_feet, created_at
            FROM properties 
            WHERE address_line1 LIKE ? OR city LIKE ? OR mls_number LIKE ?
            ORDER BY city, address_line1
            LIMIT ?
        '''
        
        search_pattern = f"%{search_term}%"
        results = conn.execute(query, (
            search_pattern, search_pattern, search_pattern, limit
        )).fetchall()
        
        properties = []
        for row in results:
            properties.append({
                'id': row['id'],
                'full_address': f"{row['address_line1']}, {row['city']}, {row['state']} {row['zip_code']}",
                'mls_number': row['mls_number'],
                'listed_price': row['listing_price'],  # Use correct column name
                'property_type': row['property_type'],
                'bedrooms': row['bedrooms'],
                'bathrooms': row['bathrooms'],
                'square_feet': row['square_feet'],
                'raw_data': dict(row)
            })
        
        conn.close()
        return properties
        
    except Exception as e:
        print(f"Error searching properties: {e}")
        return []

def get_client_by_id(client_id: int) -> Optional[Dict]:
    """Get complete client data by ID for offer population"""
    try:
        conn = get_db_connection()
        
        result = conn.execute('''
            SELECT * FROM clients WHERE id = ?
        ''', (client_id,)).fetchone()
        
        conn.close()
        
        if result:
            return dict(result)
        return None
        
    except Exception as e:
        print(f"Error getting client {client_id}: {e}")
        return None

def get_property_by_id(property_id: int) -> Optional[Dict]:
    """Get complete property data by ID for offer population"""
    try:
        conn = get_db_connection()
        
        result = conn.execute('''
            SELECT * FROM properties WHERE id = ?
        ''', (property_id,)).fetchone()
        
        conn.close()
        
        if result:
            return dict(result)
        return None
        
    except Exception as e:
        print(f"Error getting property {property_id}: {e}")
        return None

def get_agents_list(limit: int = 20) -> List[Dict]:
    """Get list of available agents for selection"""
    try:
        conn = get_db_connection()
        
        results = conn.execute('''
            SELECT id, firm_name, agent_name, agent_phone, agent_email, role
            FROM brokers_agents
            ORDER BY firm_name, agent_name
            LIMIT ?
        ''', (limit,)).fetchall()
        
        agents = []
        for row in results:
            agents.append({
                'id': row['id'],
                'display_name': f"{row['agent_name']} - {row['firm_name']}",
                'phone': row['agent_phone'],
                'email': row['agent_email'],
                'role': row['role'],
                'raw_data': dict(row)
            })
        
        conn.close()
        return agents
        
    except Exception as e:
        print(f"Error getting agents: {e}")
        return []

def get_lenders_list(limit: int = 10) -> List[Dict]:
    """Get list of available lenders for selection"""
    try:
        conn = get_db_connection()
        
        results = conn.execute('''
            SELECT id, company_name, officer_name, phone, officer_email, mortgage_type
            FROM lenders
            ORDER BY company_name
            LIMIT ?
        ''', (limit,)).fetchall()
        
        lenders = []
        for row in results:
            lenders.append({
                'id': row['id'],
                'display_name': f"{row['company_name']} - {row['officer_name'] or 'No Officer'}",
                'phone': row['phone'],
                'email': row['officer_email'],
                'mortgage_type': row['mortgage_type'],
                'raw_data': dict(row)
            })
        
        conn.close()
        return lenders
        
    except Exception as e:
        print(f"Error getting lenders: {e}")
        return []

# ============================================================================
# OFFER DATA COMPILATION FUNCTIONS
# ============================================================================

def compile_offer_data(buyer_client_id: int, property_id: int, offer_terms: Dict, 
                      agent_id: int = None, lender_id: int = None) -> Dict:
    """
    Compile complete offer data from CRM for PDF population
    
    Args:
        buyer_client_id: Primary buyer client ID
        property_id: Property ID
        offer_terms: Financial and timeline terms
        agent_id: Representing agent ID (optional)
        lender_id: Lender ID (optional)
        
    Returns:
        Complete offer data structure ready for PDF population
    """
    
    # Get all required data
    buyer_data = get_client_by_id(buyer_client_id)
    property_data = get_property_by_id(property_id)
    agent_data = None
    lender_data = None
    
    if agent_id:
        conn = get_db_connection()
        agent_result = conn.execute('SELECT * FROM brokers_agents WHERE id = ?', (agent_id,)).fetchone()
        agent_data = dict(agent_result) if agent_result else None
        conn.close()
    
    if lender_id:
        conn = get_db_connection()
        lender_result = conn.execute('SELECT * FROM lenders WHERE id = ?', (lender_id,)).fetchone()
        lender_data = dict(lender_result) if lender_result else None
        conn.close()
    
    # Compile complete offer data structure
    offer_data = {
        'buyer': buyer_data,
        'property': property_data,
        'terms': offer_terms,
        'agent': agent_data,
        'lender': lender_data,
        'generated_date': datetime.now().isoformat(),
        'form_type': 'ca_rpa'
    }
    
    return offer_data

def validate_offer_data(offer_data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate that offer data is complete for PDF generation
    
    Args:
        offer_data: Compiled offer data
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    
    errors = []
    
    # Check buyer data
    if not offer_data.get('buyer'):
        errors.append("Buyer client data is missing")
    elif not offer_data['buyer'].get('first_name') or not offer_data['buyer'].get('last_name'):
        errors.append("Buyer name is incomplete")
    
    # Check property data
    if not offer_data.get('property'):
        errors.append("Property data is missing")
    elif not offer_data['property'].get('address_line1'):
        errors.append("Property address is missing")
    
    # Check offer terms
    terms = offer_data.get('terms', {})
    if not terms.get('purchase_price'):
        errors.append("Purchase price is required")
    if not terms.get('closing_date'):
        errors.append("Closing date is required")
    
    return len(errors) == 0, errors

# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_retrieval_functions():
    """Test all retrieval functions with sample data"""
    print("🧪 Testing Database Retrieval Functions")
    print("=" * 50)
    
    # Test client search
    print("\n1. Testing client search...")
    clients = search_clients("test", limit=5)
    print(f"Found {len(clients)} clients")
    for client in clients[:2]:
        print(f"  - {client['full_name']} ({client['email']})")
    
    # Test property search
    print("\n2. Testing property search...")
    properties = search_properties("main", limit=5)
    print(f"Found {len(properties)} properties")
    for prop in properties[:2]:
        print(f"  - {prop['full_address']} (${prop['listed_price'] or 'No price'})")
    
    # Test agents list
    print("\n3. Testing agents list...")
    agents = get_agents_list(limit=3)
    print(f"Found {len(agents)} agents")
    for agent in agents:
        print(f"  - {agent['display_name']}")
    
    print("\n✅ Retrieval functions test complete")

if __name__ == "__main__":
    test_retrieval_functions()