#!/usr/bin/env python3
"""
AI-Callable Functions for Offer Creation
Extends the existing ZipForm AI functions with offer-specific capabilities
"""

import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import sys
import os

# Add the parent directory to the path to import from core_app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from offer_creation_workflow import (
    OfferCreationWorkflow, search_clients, search_properties, 
    get_client_by_id, get_property_by_id, get_agents_list, get_lenders_list,
    compile_offer_data, validate_offer_data
)
from zipform_ai_functions import get_db_connection

# ============================================================================
# AI-CALLABLE OFFER CREATION FUNCTIONS
# ============================================================================

def search_for_clients(search_term: str, limit: int = 5) -> Dict:
    """
    AI function to search for clients by name, email, or phone
    
    Args:
        search_term: What to search for (name, email, phone)
        limit: Maximum number of results
        
    Returns:
        Dictionary with success status and client list
    """
    try:
        clients = search_clients(search_term, limit)
        
        return {
            'success': True,
            'clients': clients,
            'count': len(clients),
            'message': f'Found {len(clients)} clients matching "{search_term}"'
        }
        
    except Exception as e:
        return {
            'success': False,
            'clients': [],
            'count': 0,
            'message': f'Error searching clients: {str(e)}'
        }

def search_for_properties(search_term: str, limit: int = 5) -> Dict:
    """
    AI function to search for properties by address or MLS number
    
    Args:
        search_term: What to search for (address, city, MLS)
        limit: Maximum number of results
        
    Returns:
        Dictionary with success status and property list
    """
    try:
        properties = search_properties(search_term, limit)
        
        return {
            'success': True,
            'properties': properties,
            'count': len(properties),
            'message': f'Found {len(properties)} properties matching "{search_term}"'
        }
        
    except Exception as e:
        return {
            'success': False,
            'properties': [],
            'count': 0,
            'message': f'Error searching properties: {str(e)}'
        }

def create_purchase_offer(buyer_client_id: int, property_id: int, offer_price: float, 
                         closing_date: str, **kwargs) -> Dict:
    """
    AI function to create a complete purchase offer
    
    Args:
        buyer_client_id: ID of the buyer client
        property_id: ID of the property
        offer_price: Purchase offer amount
        closing_date: Desired closing date (YYYY-MM-DD format)
        **kwargs: Additional offer terms (down_payment, earnest_money, etc.)
        
    Returns:
        Dictionary with success status and offer details
    """
    try:
        # Validate required data exists
        buyer_data = get_client_by_id(buyer_client_id)
        property_data = get_property_by_id(property_id)
        
        if not buyer_data:
            return {
                'success': False,
                'offer_id': None,
                'message': f'Buyer client ID {buyer_client_id} not found'
            }
            
        if not property_data:
            return {
                'success': False, 
                'offer_id': None,
                'message': f'Property ID {property_id} not found'
            }
        
        # Compile offer terms
        offer_terms = {
            'purchase_price': float(offer_price),
            'closing_date': closing_date,
            'down_payment': kwargs.get('down_payment', offer_price * 0.20),  # Default 20%
            'earnest_money': kwargs.get('earnest_money', offer_price * 0.01),  # Default 1%
            'financing_contingency_days': kwargs.get('financing_contingency_days', 17),
            'inspection_contingency_days': kwargs.get('inspection_contingency_days', 17),
            'appraisal_contingency_days': kwargs.get('appraisal_contingency_days', 17),
            'offer_expiration_days': kwargs.get('offer_expiration_days', 3),
            'loan_type': kwargs.get('loan_type', 'Conventional'),
            'as_is_sale': kwargs.get('as_is_sale', False),
            'home_warranty': kwargs.get('home_warranty', False)
        }
        
        # Get agent and lender if specified
        agent_id = kwargs.get('agent_id')
        lender_id = kwargs.get('lender_id')
        
        # Compile complete offer data
        complete_offer_data = compile_offer_data(
            buyer_client_id, property_id, offer_terms, agent_id, lender_id
        )
        
        # Validate offer data
        is_valid, validation_errors = validate_offer_data(complete_offer_data)
        
        if not is_valid:
            return {
                'success': False,
                'offer_id': None,
                'message': f'Offer validation failed: {"; ".join(validation_errors)}',
                'validation_errors': validation_errors
            }
        
        # Save offer to database
        conn = get_db_connection()
        workflow_id = f"offer_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{buyer_client_id}_{property_id}"
        
        cursor = conn.execute('''
            INSERT INTO offers (
                workflow_id, form_type, buyer_client_id, property_id, 
                agent_id, lender_id, offer_terms, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            workflow_id, 'ca_rpa', buyer_client_id, property_id,
            agent_id, lender_id, json.dumps(offer_terms), 'draft', datetime.now()
        ))
        
        offer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'offer_id': offer_id,
            'workflow_id': workflow_id,
            'message': f'Created offer for {buyer_data["first_name"]} {buyer_data["last_name"]} on {property_data["address_line1"]}',
            'offer_summary': {
                'buyer': f'{buyer_data["first_name"]} {buyer_data["last_name"]}',
                'property': f'{property_data["address_line1"]}, {property_data["city"]}',
                'offer_price': f'${offer_price:,.2f}',
                'down_payment': f'${offer_terms["down_payment"]:,.2f}',
                'closing_date': closing_date,
                'contingencies': f'{offer_terms["financing_contingency_days"]} days financing, {offer_terms["inspection_contingency_days"]} days inspection'
            },
            'next_steps': [
                'Review offer terms for accuracy',
                'Generate PDF document',
                'Get buyer approval and signature',
                'Submit to listing agent'
            ]
        }
        
    except Exception as e:
        return {
            'success': False,
            'offer_id': None,
            'message': f'Error creating offer: {str(e)}'
        }

def get_offer_status(offer_id: int) -> Dict:
    """
    AI function to get the status of an existing offer
    
    Args:
        offer_id: ID of the offer to check
        
    Returns:
        Dictionary with offer status and details
    """
    try:
        conn = get_db_connection()
        
        result = conn.execute('''
            SELECT o.*, c.first_name, c.last_name, p.address_line1, p.city
            FROM offers o
            JOIN clients c ON o.buyer_client_id = c.id
            JOIN properties p ON o.property_id = p.id
            WHERE o.id = ?
        ''', (offer_id,)).fetchone()
        
        conn.close()
        
        if not result:
            return {
                'success': False,
                'message': f'Offer ID {offer_id} not found'
            }
        
        offer_terms = json.loads(result['offer_terms']) if result['offer_terms'] else {}
        
        return {
            'success': True,
            'offer_id': offer_id,
            'workflow_id': result['workflow_id'],
            'status': result['status'],
            'buyer': f"{result['first_name']} {result['last_name']}",
            'property': f"{result['address_line1']}, {result['city']}",
            'offer_price': offer_terms.get('purchase_price'),
            'closing_date': offer_terms.get('closing_date'),
            'created_at': result['created_at'],
            'pdf_path': result['pdf_path'],
            'message': f'Offer {offer_id} is currently {result["status"]}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error getting offer status: {str(e)}'
        }

def list_recent_offers(limit: int = 10) -> Dict:
    """
    AI function to list recent offers with their status
    
    Args:
        limit: Maximum number of offers to return
        
    Returns:
        Dictionary with list of recent offers
    """
    try:
        conn = get_db_connection()
        
        results = conn.execute('''
            SELECT o.id, o.workflow_id, o.status, o.created_at,
                   c.first_name, c.last_name, p.address_line1, p.city,
                   o.offer_terms
            FROM offers o
            JOIN clients c ON o.buyer_client_id = c.id
            JOIN properties p ON o.property_id = p.id
            ORDER BY o.created_at DESC
            LIMIT ?
        ''', (limit,)).fetchall()
        
        conn.close()
        
        offers = []
        for row in results:
            offer_terms = json.loads(row['offer_terms']) if row['offer_terms'] else {}
            offers.append({
                'id': row['id'],
                'workflow_id': row['workflow_id'],
                'status': row['status'],
                'buyer': f"{row['first_name']} {row['last_name']}",
                'property': f"{row['address_line1']}, {row['city']}",
                'offer_price': offer_terms.get('purchase_price'),
                'created_at': row['created_at']
            })
        
        return {
            'success': True,
            'offers': offers,
            'count': len(offers),
            'message': f'Found {len(offers)} recent offers'
        }
        
    except Exception as e:
        return {
            'success': False,
            'offers': [],
            'count': 0,
            'message': f'Error listing offers: {str(e)}'
        }

# ============================================================================
# OFFER CREATION AI FUNCTION REGISTRY
# ============================================================================

OFFER_CREATION_AI_FUNCTIONS = {
    'search_for_clients': {
        'function': search_for_clients,
        'description': 'Search for clients by name, email, or phone number',
        'required_params': ['search_term'],
        'optional_params': ['limit'],
        'example': 'search_for_clients("John Smith") or search_for_clients("john@email.com")'
    },
    'search_for_properties': {
        'function': search_for_properties,
        'description': 'Search for properties by address, city, or MLS number', 
        'required_params': ['search_term'],
        'optional_params': ['limit'],
        'example': 'search_for_properties("123 Main St") or search_for_properties("Sacramento")'
    },
    'create_purchase_offer': {
        'function': create_purchase_offer,
        'description': 'Create a complete purchase offer with buyer, property, and terms',
        'required_params': ['buyer_client_id', 'property_id', 'offer_price', 'closing_date'],
        'optional_params': ['down_payment', 'earnest_money', 'agent_id', 'lender_id', 'financing_contingency_days', 'inspection_contingency_days'],
        'example': 'create_purchase_offer(1, 2, 550000, "2024-03-15", down_payment=110000, earnest_money=5500)'
    },
    'get_offer_status': {
        'function': get_offer_status,
        'description': 'Get the current status and details of an existing offer',
        'required_params': ['offer_id'],
        'optional_params': [],
        'example': 'get_offer_status(123)'
    },
    'list_recent_offers': {
        'function': list_recent_offers,
        'description': 'List recent offers with their status and basic details',
        'required_params': [],
        'optional_params': ['limit'],
        'example': 'list_recent_offers() or list_recent_offers(limit=5)'
    }
}

if __name__ == "__main__":
    print("🏠 Offer Creation AI Functions Ready")
    print("=" * 50)
    print("Available offer creation functions:")
    for func_name, info in OFFER_CREATION_AI_FUNCTIONS.items():
        print(f"  {func_name}: {info['description']}")
    
    # Test with sample data
    print("\n🧪 Testing with sample data...")
    
    # Test client search
    result = search_for_clients("John")
    print(f"\nClient search result: {result['count']} clients found")
    
    # Test property search  
    result = search_for_properties("Main")
    print(f"Property search result: {result['count']} properties found")
    
    if result['count'] > 0:
        # Test offer creation
        print("\n📝 Testing offer creation...")
        offer_result = create_purchase_offer(
            buyer_client_id=1, 
            property_id=1, 
            offer_price=550000,
            closing_date="2024-02-15",
            down_payment=110000,
            earnest_money=5500
        )
        print(f"Offer creation: {offer_result['message']}")
        
        if offer_result['success']:
            # Test offer status
            status_result = get_offer_status(offer_result['offer_id'])
            print(f"Offer status: {status_result['message']}")
    
    print("\n✅ Offer creation functions test complete")