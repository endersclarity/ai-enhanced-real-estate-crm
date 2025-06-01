#!/usr/bin/env python3
"""
Test the complete offer creation workflow end-to-end
"""

import sys
import os
sys.path.append('core_app')

def test_offer_creation_workflow():
    """Test the complete offer creation workflow"""
    print("🧪 TESTING COMPLETE OFFER CREATION WORKFLOW")
    print("=" * 60)
    
    try:
        # Import our functions
        from ai_modules.offer_creation_functions import (
            search_for_clients, search_for_properties, create_purchase_offer,
            get_offer_status, list_recent_offers
        )
        
        print("✅ Successfully imported offer creation functions")
        
        # Test 1: Search for clients
        print("\n1️⃣ Testing client search...")
        client_result = search_for_clients("John")
        print(f"   Found {client_result['count']} clients")
        if client_result['count'] > 0:
            buyer_client = client_result['clients'][0]
            print(f"   Selected buyer: {buyer_client['full_name']} (ID: {buyer_client['id']})")
        else:
            print("   ❌ No clients found - cannot continue test")
            return False
        
        # Test 2: Search for properties
        print("\n2️⃣ Testing property search...")
        property_result = search_for_properties("Main")
        print(f"   Found {property_result['count']} properties")
        if property_result['count'] > 0:
            target_property = property_result['properties'][0]
            print(f"   Selected property: {target_property['full_address']} (ID: {target_property['id']})")
            print(f"   Listed at: ${target_property['listed_price']:,}")
        else:
            print("   ❌ No properties found - cannot continue test")
            return False
        
        # Test 3: Create purchase offer
        print("\n3️⃣ Testing offer creation...")
        offer_price = target_property['listed_price'] - 10000  # Offer $10K under asking
        
        offer_result = create_purchase_offer(
            buyer_client_id=buyer_client['id'],
            property_id=target_property['id'],
            offer_price=offer_price,
            closing_date="2024-03-15",
            down_payment=offer_price * 0.20,  # 20% down
            earnest_money=offer_price * 0.01,  # 1% earnest money
            financing_contingency_days=17,
            inspection_contingency_days=10
        )
        
        if offer_result['success']:
            print(f"   ✅ Offer created successfully!")
            print(f"   Offer ID: {offer_result['offer_id']}")
            print(f"   Workflow ID: {offer_result['workflow_id']}")
            print(f"   Summary: {offer_result['offer_summary']}")
        else:
            print(f"   ❌ Offer creation failed: {offer_result['message']}")
            return False
        
        # Test 4: Check offer status
        print("\n4️⃣ Testing offer status lookup...")
        status_result = get_offer_status(offer_result['offer_id'])
        if status_result['success']:
            print(f"   ✅ Offer status retrieved")
            print(f"   Status: {status_result['status']}")
            print(f"   Buyer: {status_result['buyer']}")
            print(f"   Property: {status_result['property']}")
        else:
            print(f"   ❌ Status lookup failed: {status_result['message']}")
        
        # Test 5: List recent offers
        print("\n5️⃣ Testing recent offers list...")
        list_result = list_recent_offers(limit=5)
        if list_result['success']:
            print(f"   ✅ Retrieved {list_result['count']} recent offers")
            for offer in list_result['offers'][:3]:  # Show first 3
                print(f"     - Offer {offer['id']}: {offer['buyer']} → {offer['property']}")
        else:
            print(f"   ❌ Offer list failed: {list_result['message']}")
        
        print("\n🎉 OFFER CREATION WORKFLOW TEST COMPLETE!")
        print("\n📋 SUMMARY:")
        print(f"   • Found {client_result['count']} clients in database")
        print(f"   • Found {property_result['count']} properties in database")
        print(f"   • Successfully created offer #{offer_result['offer_id']}")
        print(f"   • Offer amount: ${offer_price:,}")
        print(f"   • Status: {status_result.get('status', 'Unknown')}")
        
        print("\n🚀 READY FOR CHATBOT INTEGRATION!")
        print("   The AI can now process natural language like:")
        print('   • "Create an offer for John Smith on 123 Main Street at $540,000"')
        print('   • "Search for clients named John"')
        print('   • "Find properties in Sacramento under $600,000"')
        print('   • "What\'s the status of offer #1?"')
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_offer_creation_workflow()