#!/usr/bin/env python3
"""
Test script for Nevada County MLS Integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Install pandas if needed
try:
    import pandas as pd
except ImportError:
    print("Installing pandas...")
    os.system("pip install pandas")
    import pandas as pd

from mls_integration import (
    load_mls_data, find_mls_property, create_property_from_mls, 
    get_mls_status, MLS_FUNCTIONS
)

def test_mls_integration():
    """Test Nevada County MLS integration with sample data"""
    print("🏠 Testing Nevada County MLS Integration")
    print("="*60)
    
    # Test 1: Load MLS data
    print("1. Loading MLS data from sample CSV...")
    result = load_mls_data('test_mls_sample.csv')
    print(f"   Result: {result}")
    
    if not result['success']:
        print("❌ Failed to load MLS data, stopping tests")
        return
    
    # Test 2: Check MLS status
    print("\n2. Checking MLS status...")
    status = get_mls_status()
    print(f"   Status: {status}")
    
    # Test 3: Find specific MLS property
    print("\n3. Finding MLS property #223040162...")
    property_result = find_mls_property("223040162")
    print(f"   Found: {property_result['success']}")
    if property_result['success']:
        prop = property_result['property']
        print(f"   Address: {prop.get('Address - Street Complete')}, {prop.get('Address - City')}")
        print(f"   Price: ${prop.get('Current Listing Price'):,}")
        print(f"   Bedrooms: {prop.get('Bedrooms And Possible Bedrooms')}")
        print(f"   Square Feet: {prop.get('Square Footage')}")
    
    # Test 4: Create property from MLS data
    print("\n4. Creating property record from MLS #223040162...")
    create_result = create_property_from_mls("223040162")
    print(f"   Creation result: {create_result}")
    
    # Test 5: Test function registry
    print("\n5. Available MLS functions for AI:")
    for func_name, info in MLS_FUNCTIONS.items():
        print(f"   {func_name}: {info['description']}")
        print(f"      Example: {info['example']}")
    
    print("\n✅ MLS Integration tests completed!")

def test_conversation_flow():
    """Test conversational MLS workflow"""
    print("\n💬 Testing Conversational MLS Workflow")
    print("="*60)
    
    # Simulate AI conversation
    print("User: 'Client is interested in MLS 223040162'")
    
    # AI looks up MLS property
    mls_result = find_mls_property("223040162")
    if mls_result['success']:
        prop = mls_result['property']
        print(f"AI: 'Found MLS #223040162: {prop.get('Bedrooms And Possible Bedrooms')} bedroom house")
        print(f"     at {prop.get('Address - Street Complete')}, {prop.get('Address - City')}")
        print(f"     for ${prop.get('Current Listing Price'):,}. Want me to create a property record?'")
        
        print("\nUser: 'Yes, add it to our system'")
        
        # AI creates property record
        create_result = create_property_from_mls("223040162")
        if create_result['success']:
            print(f"AI: 'Done! Created property record ID #{create_result['property_id']}.")
            print("     All Nevada County MLS details have been imported. Want me to schedule a showing?'")
        else:
            print(f"AI: 'Sorry, couldn't create property: {create_result['message']}'")
    else:
        print(f"AI: 'Sorry, couldn't find MLS #223040162: {mls_result['message']}'")

def main():
    """Run all MLS tests"""
    test_mls_integration()
    test_conversation_flow()

if __name__ == "__main__":
    main()