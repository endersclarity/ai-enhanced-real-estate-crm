#!/usr/bin/env python3
"""
Minimum Form Requirements
Shows the absolute minimum information needed to generate each CAR form
"""

def get_minimum_requirements():
    """Get the absolute minimum info needed for each form type"""
    
    minimum_reqs = {
        "buyer_representation_agreement": {
            "form_name": "Buyer Representation Agreement",
            "usage_rate": "95%",
            "minimum_fields": {
                "client": {
                    "first_name": "Client's first name",
                    "last_name": "Client's last name", 
                    "phone": "Contact phone number",
                    "email": "Email address",
                    "address": "Full mailing address (can be one field)"
                },
                "agent": {
                    "agent_name": "Agent's full name",
                    "license_number": "Real estate license number",
                    "brokerage": "Brokerage firm name",
                    "commission_rate": "Commission percentage (e.g., 2.5%)"
                }
            },
            "total_minimum_fields": 9,
            "estimated_time": "30 seconds to fill"
        },
        
        "statewide_buyer_seller_advisory": {
            "form_name": "Statewide Buyer/Seller Advisory", 
            "usage_rate": "90%",
            "minimum_fields": {
                "client": {
                    "full_name": "Client's full name",
                    "phone": "Contact phone",
                    "email": "Email address"
                },
                "property": {
                    "address": "Property address",
                    "city": "Property city", 
                    "property_type": "Type (house, condo, etc.)"
                },
                "transaction": {
                    "transaction_type": "Buy, sell, or lease"
                }
            },
            "total_minimum_fields": 7,
            "estimated_time": "20 seconds to fill"
        },
        
        "agent_visual_inspection_disclosure": {
            "form_name": "Agent Visual Inspection Disclosure",
            "usage_rate": "75%", 
            "minimum_fields": {
                "client": {
                    "full_name": "Client's full name"
                },
                "property": {
                    "address": "Property address",
                    "city": "Property city",
                    "property_type": "Property type"
                },
                "inspection": {
                    "inspection_date": "Date of inspection"
                },
                "agent": {
                    "agent_name": "Inspecting agent name",
                    "license_number": "Agent license number",
                    "brokerage": "Brokerage name"
                }
            },
            "total_minimum_fields": 8,
            "estimated_time": "25 seconds to fill"
        },
        
        "transaction_record": {
            "form_name": "Transaction Record",
            "usage_rate": "85%",
            "minimum_fields": {
                "client": {
                    "full_name": "Buyer's full name",
                    "phone": "Contact phone",
                    "email": "Email address"
                },
                "property": {
                    "address": "Property address"
                },
                "transaction": {
                    "purchase_price": "Purchase price ($)",
                    "earnest_money": "Earnest money amount ($)",
                    "contract_date": "Contract date",
                    "closing_date": "Closing date",
                    "listing_agent": "Listing agent name",
                    "buyer_agent": "Buyer's agent name"
                }
            },
            "total_minimum_fields": 10,
            "estimated_time": "45 seconds to fill"
        },
        
        "market_conditions_advisory": {
            "form_name": "Market Conditions Advisory",
            "usage_rate": "70%",
            "minimum_fields": {
                "client": {
                    "full_name": "Client's full name",
                    "phone": "Contact phone", 
                    "email": "Email address"
                },
                "market": {
                    "target_city": "Target market city",
                    "property_type": "Property type of interest",
                    "transaction_type": "Transaction type (buy/sell)"
                },
                "agent": {
                    "agent_name": "Agent's full name",
                    "license_number": "License number",
                    "brokerage": "Brokerage name"
                }
            },
            "total_minimum_fields": 9,
            "estimated_time": "30 seconds to fill"
        }
    }
    
    return minimum_reqs

def print_all_minimums():
    """Print a clean summary of minimum requirements for all forms"""
    reqs = get_minimum_requirements()
    
    print("🎯 MINIMUM REQUIRED INFO FOR CAR FORMS")
    print("=" * 60)
    print("(Fastest possible form generation)")
    print()
    
    for form_id, form_data in reqs.items():
        print(f"📋 {form_data['form_name']} ({form_data['usage_rate']} usage)")
        print(f"   ⏱️  {form_data['estimated_time']} | 📊 {form_data['total_minimum_fields']} fields")
        
        for category, fields in form_data['minimum_fields'].items():
            print(f"   {category.title()}:")
            for field_name, description in fields.items():
                print(f"     • {description}")
        print()

def get_ultra_minimum():
    """Get the absolute bare minimum for quick form generation"""
    
    ultra_minimum = {
        "ANY_FORM": {
            "client_name": "Required for all forms",
            "agent_name": "Required for all forms", 
            "agent_license": "Required for compliance"
        },
        
        "PROPERTY_FORMS": {
            "property_address": "Required when property is involved"
        },
        
        "TRANSACTION_FORMS": {
            "purchase_price": "Required for purchase agreements",
            "closing_date": "Required for transaction tracking"
        }
    }
    
    print("⚡ ULTRA-MINIMUM (Emergency Form Generation)")
    print("=" * 50)
    print("Just 3-6 fields can generate most forms:")
    print()
    
    for category, fields in ultra_minimum.items():
        print(f"{category}:")
        for field, desc in fields.items():
            print(f"  • {field}: {desc}")
        print()

if __name__ == "__main__":
    print_all_minimums()
    print()
    get_ultra_minimum()