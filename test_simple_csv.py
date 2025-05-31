#!/usr/bin/env python3
"""
Test the practical 14-field CSV structure
"""

import csv
import json

def test_simple_csv():
    print("🏠 SIMPLE CSV VALIDATION")
    print("=" * 40)
    
    # Load practical CSV
    with open('practical_offer_template.csv', 'r') as f:
        reader = csv.DictReader(f)
        data = next(reader)
    
    # Load simple mapping
    with open('simple_field_mapping.json', 'r') as f:
        mapping = json.load(f)
    
    print(f"✅ Loaded CSV with {len(data)} fields")
    print(f"✅ Expected {mapping['csv_structure']['total_fields']} fields")
    
    # Check required fields
    required = mapping['validation_rules']['required_fields']
    missing = [f for f in required if not data.get(f) or not data[f].strip()]
    
    print(f"\n📊 VALIDATION:")
    print(f"   Required fields: {len(required)}")
    print(f"   Missing/empty: {len(missing)}")
    
    if missing:
        print(f"   ❌ Missing: {missing}")
    else:
        print(f"   ✅ All required fields populated")
    
    # Show sample data
    print(f"\n🎯 SAMPLE DATA:")
    key_fields = ['buyer_name', 'property_address', 'offer_price', 'earnest_money']
    for field in key_fields:
        print(f"   {field}: {data.get(field, 'MISSING')}")
    
    print(f"\n✅ Simple CSV structure ready for form generation!")
    return len(missing) == 0

if __name__ == "__main__":
    success = test_simple_csv()
    print(f"\nResult: {'PASS' if success else 'FAIL'}")