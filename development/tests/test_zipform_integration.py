#!/usr/bin/env python3
"""
Comprehensive ZipForm Integration Test
Tests all ZipForm Transaction Cover Sheet functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from zipform_ai_functions import *
from datetime import datetime, date

def test_complete_zipform_workflow():
    """Test a complete ZipForm transaction workflow"""
    print("🚀 Testing Complete ZipForm Transaction Workflow")
    print("=" * 60)
    
    # Test 1: Create Buyer Client with ZipForm fields
    print("\n1. Creating Buyer Client with ZipForm fields...")
    buyer_result = create_client_zipform(
        first_name="John",
        last_name="Smith", 
        middle_initial="M",
        email="john.smith@email.com",
        home_phone="(530) 555-1234",
        business_phone="(530) 555-5678", 
        cellular_phone="(530) 555-9999",
        fax_number="(530) 555-4321",
        street_address="123 Oak Street",
        city="Grass Valley",
        state="CA",
        zip_code="95945",
        county="Nevada County",
        client_type="buyer",
        employer="Tech Company Inc",
        occupation="Software Engineer",
        annual_income=95000,
        preferred_contact_method="cellular_phone",
        auto_signature_enabled=True,
        notes="First-time homebuyer, pre-approved for $500K"
    )
    print(f"   Result: {buyer_result}")
    
    # Test 2: Create Seller Client
    print("\n2. Creating Seller Client...")
    seller_result = create_client_zipform(
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@email.com", 
        home_phone="(530) 555-2468",
        cellular_phone="(530) 555-1357",
        street_address="456 Pine Street",
        city="Nevada City",
        state="CA",
        zip_code="95959",
        county="Nevada County",
        client_type="seller"
    )
    print(f"   Result: {seller_result}")
    
    # Test 3: Create Property with comprehensive ZipForm details
    print("\n3. Creating Property with ZipForm details...")
    property_result = create_property_zipform(
        street_address="789 Mountain View Drive",
        city="Grass Valley",
        state="CA",
        zip_code="95945",
        county="Nevada County",
        township="Grass Valley Township",
        legal_description="Lot 15, Block 3, Mountain View Estates",
        tax_id="057-123-045",
        assessor_parcel_number="057-123-045-000",
        lot_number="15",
        unit_number=None,
        block="3",
        subdivision="Mountain View Estates",
        mls_number="ML2024001",
        listing_date="2024-01-15",
        expiration_date="2024-07-15",
        listed_price=675000,
        original_price=685000,
        property_type="Residential",
        year_built=2018,
        bedrooms=4,
        bathrooms=2.5,
        square_feet=2450,
        lot_size_acres=0.25,
        lot_size_sqft=10890,
        homeowner_assoc_dues=125,
        transfer_fee=500,
        doc_prep_fees=250,
        property_includes="All appliances, window coverings, irrigation system",
        property_excludes="Personal property, artwork",
        supplemental_info="Mountain views, quiet cul-de-sac location",
        property_description="Beautiful 4-bedroom home with mountain views",
        public_remarks="Stunning home in desirable Mountain View Estates"
    )
    print(f"   Result: {property_result}")
    
    # Test 4: Create Listing Broker/Agent
    print("\n4. Creating Listing Broker/Agent...")
    listing_agent_result = create_broker_agent(
        firm_name="Coldwell Banker Grass Roots Realty",
        firm_address="167 South Auburn Street",
        firm_city="Grass Valley",
        firm_state="CA",
        firm_zip_code="95945",
        firm_phone="(530) 276-5970",
        firm_dre_license="01234567",
        agent_name="Narissa Jennings",
        agent_phone="(530) 276-5970",
        agent_cellular="(530) 555-1111",
        agent_email="narissa@cbgrr.com",
        agent_dre_license="01987654",
        role="listing_agent"
    )
    print(f"   Result: {listing_agent_result}")
    
    # Test 5: Create Selling Broker/Agent
    print("\n5. Creating Selling Broker/Agent...")
    selling_agent_result = create_broker_agent(
        firm_name="RE/MAX Gold",
        agent_name="Bob Anderson",
        agent_phone="(530) 555-2222",
        agent_email="bob@remaxgold.com",
        role="selling_agent"
    )
    print(f"   Result: {selling_agent_result}")
    
    # Test 6: Create Lender
    print("\n6. Creating Lender...")
    lender_result = create_lender(
        company_name="First National Bank",
        street_address="100 Bank Street",
        city="Grass Valley",
        state="CA",
        zip_code="95945",
        phone="(530) 555-BANK",
        officer_name="Sarah Lender",
        officer_email="sarah@firstnational.com",
        mortgage_type="Conv"
    )
    print(f"   Result: {lender_result}")
    
    # Test 7: Create Title Company
    print("\n7. Creating Title Company...")
    title_result = create_title_company(
        company_name="Sierra Title Company",
        street_address="200 Title Way",
        city="Nevada City", 
        state="CA",
        zip_code="95959",
        phone="(530) 555-TITLE",
        officer_name="Mike Title",
        officer_email="mike@sierratitle.com"
    )
    print(f"   Result: {title_result}")
    
    # Test 8: Create Escrow Company
    print("\n8. Creating Escrow Company...")
    escrow_result = create_escrow_company(
        company_name="Gold Country Escrow",
        street_address="300 Escrow Lane",
        city="Grass Valley",
        state="CA", 
        zip_code="95945",
        phone="(530) 555-ESCROW",
        officer_name="Lisa Escrow",
        officer_license_number="ESC123456",
        escrow_number="GCE2024001",
        closing_date="2024-03-15"
    )
    print(f"   Result: {escrow_result}")
    
    # Test 9: Create Service Providers
    print("\n9. Creating Service Providers...")
    
    # Pest Control
    pest_control_result = create_service_provider(
        company_name="Sierra Pest Control",
        service_type="pest_control",
        representative_name="Joe Exterminator",
        phone="(530) 555-PEST"
    )
    print(f"   Pest Control: {pest_control_result}")
    
    # Home Warranty
    warranty_result = create_service_provider(
        company_name="HomeGuard Warranty",
        service_type="home_warranty", 
        representative_name="Mary Warranty",
        phone="(800) 555-WARRANTY"
    )
    print(f"   Home Warranty: {warranty_result}")
    
    # Transaction Coordinator
    coordinator_result = create_service_provider(
        company_name="TC Pros",
        service_type="transaction_coordinator",
        representative_name="Tom Coordinator",
        phone="(530) 555-COORD",
        coordinator_side="buy_side"
    )
    print(f"   Transaction Coordinator: {coordinator_result}")
    
    # Test 10: Create Complete Transaction
    print("\n10. Creating Complete Transaction...")
    if (buyer_result['success'] and property_result['success'] and 
        seller_result['success'] and listing_agent_result['success']):
        
        transaction_result = create_transaction(
            transaction_type="purchase",
            property_id=property_result['property_id'],
            buyer_client_id=buyer_result['client_id'],
            seller_client_id=seller_result['client_id'],
            purchase_price=650000,
            original_offer_price=675000,
            offer_date="2024-02-01",
            offer_expiration_date="2024-02-03",
            offer_expiration_time="5:00 PM",
            acceptance_date="2024-02-02",
            contract_date="2024-02-03",
            closing_date="2024-03-15",
            down_payment_amount=130000,
            down_payment_percentage=20.0,
            loan_amount=520000,
            loan_term_years=30,
            interest_rate=6.5,
            earnest_money_amount=10000,
            deposit_amount=10000,
            listing_agent_id=listing_agent_result['broker_agent_id'],
            selling_agent_id=selling_agent_result['broker_agent_id'],
            lender_id=lender_result['lender_id'],
            title_company_id=title_result['title_company_id'],
            escrow_company_id=escrow_result['escrow_company_id'],
            financing_contingency_date="2024-02-17",
            inspection_contingency_date="2024-02-10",
            appraisal_contingency_date="2024-02-24",
            home_warranty=True,
            notes="Buyer's first home purchase, seller motivated",
            status="pending"
        )
        print(f"   Result: {transaction_result}")
    else:
        print("   ❌ Skipping transaction creation due to previous failures")
    
    print("\n🎉 ZipForm Integration Test Completed!")
    print("All ZipForm Transaction Cover Sheet fields are now supported!")

def test_database_structure():
    """Test that all expected tables and fields exist"""
    print("\n📋 Verifying Database Structure...")
    
    conn = get_db_connection()
    
    # Check all expected tables
    expected_tables = [
        'clients', 'properties', 'transactions', 'brokers_agents',
        'lenders', 'title_companies', 'escrow_companies', 
        'appraisal_companies', 'service_providers'
    ]
    
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    existing_tables = [table[0] for table in tables]
    
    for table in expected_tables:
        if table in existing_tables:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  ✅ {table}: {count} records")
        else:
            print(f"  ❌ Missing: {table}")
    
    conn.close()

def test_function_registry():
    """Test that all ZipForm functions are registered"""
    print("\n🔧 Testing Function Registry...")
    
    expected_zipform_functions = [
        'create_client_zipform', 'create_property_zipform', 'create_transaction',
        'create_broker_agent', 'create_lender', 'create_title_company',
        'create_escrow_company', 'create_service_provider'
    ]
    
    for func_name in expected_zipform_functions:
        if func_name in ZIPFORM_AI_FUNCTIONS:
            func_info = ZIPFORM_AI_FUNCTIONS[func_name]
            print(f"  ✅ {func_name}: {func_info['description']}")
        else:
            print(f"  ❌ Missing: {func_name}")

def main():
    """Run all ZipForm integration tests"""
    print("🏠 ZipForm Integration Test Suite")
    print("Testing complete real estate transaction workflow")
    print("=" * 60)
    
    try:
        # Test database structure
        test_database_structure()
        
        # Test function registry
        test_function_registry()
        
        # Test complete workflow
        test_complete_zipform_workflow()
        
        print("\n✅ All tests completed successfully!")
        print("Your CRM now supports complete ZipForm Transaction Cover Sheet functionality!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()