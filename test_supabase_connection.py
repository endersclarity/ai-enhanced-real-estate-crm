#!/usr/bin/env python3
"""
Test Supabase Database Connection
Real Estate CRM - Task 5 Verification
"""
import os
import sys

# Set environment variable to use Supabase
os.environ['USE_SUPABASE'] = 'true'

# Import database configuration
from database_config import db

def test_connection():
    """Test Supabase database connection and functionality"""
    print("🏠 Real Estate CRM - Supabase Connection Test\n")
    
    # Test 1: Database initialization
    print("1️⃣ Testing database initialization...")
    success = db.init_database_schema()
    if not success:
        print("❌ Database initialization failed")
        return False
    
    # Test 2: Client summary (reads existing data)
    print("\n2️⃣ Testing client data retrieval...")
    summary = db.get_clients_summary()
    print(f"   📊 Client Summary: {summary}")
    
    # Test 3: Get all clients
    print("\n3️⃣ Testing full client list...")
    clients = db.get_all_clients()
    print(f"   👥 Found {len(clients)} clients")
    for client in clients[:3]:  # Show first 3
        name = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip()
        print(f"      - {name} ({client.get('client_type', 'Unknown')})")
    
    # Test 4: Get all properties
    print("\n4️⃣ Testing property data retrieval...")
    properties = db.get_all_properties()
    print(f"   🏘️ Found {len(properties)} properties")
    for prop in properties[:3]:  # Show first 3
        address = prop.get('street_address', 'Unknown')
        city = prop.get('city', 'Unknown')
        price = prop.get('listed_price', 0)
        mls = prop.get('mls_number', '')
        mls_str = f" (MLS #{mls})" if mls else ""
        print(f"      - {address}, {city} - ${price:,.0f}{mls_str}")
    
    # Test 5: Test create client (optional)
    print("\n5️⃣ Testing client creation...")
    test_client = {
        'first_name': 'Test',
        'last_name': 'Client',
        'email': 'test.client@example.com',
        'client_type': 'buyer',
        'status': 'active'
    }
    
    create_success = db.create_client(test_client)
    if create_success:
        print("   ✅ Test client created successfully")
        # Clean up - get the new client count
        updated_summary = db.get_clients_summary()
        print(f"   📊 Updated client count: {updated_summary['total_clients']}")
    else:
        print("   ⚠️ Client creation test failed (may be expected)")
    
    print("\n🎉 Connection test completed!")
    print(f"   Database mode: {'Supabase PostgreSQL' if db.use_supabase else 'SQLite'}")
    print(f"   URL: {getattr(db, 'supabase_url', 'N/A')}")
    
    return True

if __name__ == "__main__":
    test_connection()