#!/usr/bin/env python3
"""
Test script for AI-callable database functions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_estate_crm import (
    create_client, find_clients, update_client,
    create_property, find_properties,
    AI_CALLABLE_FUNCTIONS, init_database
)

def test_client_functions():
    """Test client management functions"""
    print("🧪 Testing Client Functions")
    print("="*50)
    
    # Test create_client
    print("1. Creating new client...")
    result = create_client(
        "John", "Smith", 
        email="john.smith@email.com",
        phone="555-1234",
        client_type="buyer",
        address_city="Sacramento",
        address_state="CA",
        occupation="Engineer"
    )
    print(f"   Result: {result}")
    client_id = result.get('client_id')
    
    # Test find_clients
    print("\n2. Searching for clients...")
    search_result = find_clients("John")
    print(f"   Found {search_result['count']} clients: {search_result['clients']}")
    
    # Test update_client
    if client_id:
        print(f"\n3. Updating client {client_id}...")
        update_result = update_client(
            client_id,
            phone_primary="555-9999",
            email="john.smith.updated@email.com"
        )
        print(f"   Result: {update_result}")
    
    # Test conflict detection
    print("\n4. Testing conflict detection...")
    conflict_result = create_client(
        "Jane", "Doe",
        email="john.smith@email.com"  # Same email as John
    )
    print(f"   Conflict result: {conflict_result}")

def test_property_functions():
    """Test property management functions"""
    print("\n🏠 Testing Property Functions")
    print("="*50)
    
    # Test create_property
    print("1. Creating new property...")
    result = create_property(
        address_line1="123 Main Street",
        city="Sacramento", 
        state="CA",
        zip_code="95814",
        listing_price=500000,
        bedrooms=3,
        bathrooms=2,
        square_feet=1800,
        property_type="single_family",
        mls_number="MLS123456"
    )
    print(f"   Result: {result}")
    
    # Test find_properties
    print("\n2. Searching for properties...")
    search_result = find_properties(city="Sacramento")
    print(f"   Found {search_result['count']} properties: {search_result['properties']}")
    
    # Test property price range search
    print("\n3. Searching by price range...")
    price_search = find_properties(min_price=400000, max_price=600000)
    print(f"   Found {price_search['count']} properties in price range")

def test_function_registry():
    """Test the AI function registry"""
    print("\n🤖 Testing Function Registry")
    print("="*50)
    
    print("Available AI-callable functions:")
    for func_name, func_info in AI_CALLABLE_FUNCTIONS.items():
        print(f"   {func_name}: {func_info['description']}")
        print(f"      Required: {func_info['required_params']}")
        print(f"      Optional: {func_info['optional_params']}")
        print(f"      Example: {func_info['example']}")
        print()

def main():
    """Run all tests"""
    print("🚀 Testing AI-Callable Database Functions")
    print("="*60)
    
    # Initialize database
    print("Initializing database...")
    init_database()
    
    # Run tests
    test_client_functions()
    test_property_functions()
    test_function_registry()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()