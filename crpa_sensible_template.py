#!/usr/bin/env python3
"""
California Residential Purchase Agreement - Sensible Template
Instead of 292,770 coordinate fields, here's what we actually need
"""

def get_crpa_essential_fields():
    """The actual fields needed for a CRPA - not coordinate madness"""
    
    crpa_template = {
        "form_name": "California Residential Purchase Agreement",
        "form_code": "RPA-CA", 
        "pages": "8-10 (not 27 - that's with all addendums)",
        "actual_essential_fields": {
            
            # PROPERTY INFORMATION (5 fields)
            "property": {
                "property_address": "123 Main St",
                "city_state_zip": "Nevada City, CA 95959", 
                "apn": "123-456-789",
                "county": "Nevada County",
                "property_type": "Single Family Residence"
            },
            
            # BUYER INFORMATION (6 fields)
            "buyer": {
                "buyer_name": "John and Jane Doe",
                "buyer_address": "456 Current St, Nevada City CA 95959",
                "buyer_phone": "(530) 555-1234",
                "buyer_email": "buyer@email.com",
                "buyer_agent": "Narissa Jennings",
                "buyer_brokerage": "Coldwell Banker Grass Roots Realty"
            },
            
            # SELLER INFORMATION (6 fields)  
            "seller": {
                "seller_name": "Bob and Betty Smith",
                "seller_address": "123 Main St, Nevada City CA 95959",
                "seller_phone": "(530) 555-5678", 
                "seller_email": "seller@email.com",
                "seller_agent": "Other Agent Name",
                "seller_brokerage": "Other Brokerage Name"
            },
            
            # PURCHASE TERMS (8 fields)
            "purchase_terms": {
                "purchase_price": "$450,000",
                "initial_deposit": "$5,000",
                "down_payment": "$90,000", 
                "loan_amount": "$360,000",
                "closing_date": "45 days from acceptance",
                "possession_date": "Close of escrow",
                "financing_contingency_days": "21",
                "inspection_contingency_days": "17"
            },
            
            # DATES (4 fields)
            "dates": {
                "offer_date": "2025-06-04",
                "offer_expiration": "2025-06-07",  
                "contract_date": "TBD",
                "closing_date": "TBD"
            },
            
            # AGENT DETAILS (4 fields)
            "agent_info": {
                "buyer_agent_license": "02129287",
                "buyer_agent_phone": "(530) 276-5970",
                "seller_agent_license": "TBD",
                "escrow_company": "Nevada County Escrow"
            }
        },
        
        "total_sensible_fields": 33,
        "estimated_fill_time": "3-5 minutes",
        "note": "This is what a REAL CRPA needs - not 292,770 coordinate points!"
    }
    
    return crpa_template

def print_sensible_crpa():
    """Show what we actually need vs the coordinate madness"""
    template = get_crpa_essential_fields()
    
    print("🏠 CALIFORNIA RESIDENTIAL PURCHASE AGREEMENT")
    print("=" * 60)
    print("SENSIBLE APPROACH vs COORDINATE MADNESS")
    print()
    
    print(f"📋 Form: {template['form_name']}")
    print(f"📄 Pages: {template['pages']}")
    print(f"📊 Essential Fields: {template['total_sensible_fields']}")
    print(f"⏱️  Fill Time: {template['estimated_fill_time']}")
    print()
    
    for category, fields in template['actual_essential_fields'].items():
        print(f"📂 {category.upper().replace('_', ' ')}")
        for field_name, example_value in fields.items():
            print(f"   • {field_name}: {example_value}")
        print()
    
    print("💡 COMPARISON:")
    print("   Coordinate approach: 292,770 fields")
    print("   Sensible approach: 33 fields")
    print("   Reduction: 99.99% fewer fields!")
    print()
    print("🎯 RESULT: Normal humans can actually fill this out!")

if __name__ == "__main__":
    print_sensible_crpa()