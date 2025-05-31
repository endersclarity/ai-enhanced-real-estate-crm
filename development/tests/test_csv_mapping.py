#!/usr/bin/env python3
"""
Test CSV field mapping validation
Tests the comprehensive 177-field CSV structure against form processing
"""

import csv
import json
import os
from datetime import datetime

def load_csv_data(csv_file):
    """Load data from CSV file"""
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data = next(reader)  # Get first (and only) data row
            return data
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def load_field_mapping(mapping_file):
    """Load field mapping configuration"""
    try:
        with open(mapping_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading mapping: {e}")
        return None

def validate_required_fields(data, mapping):
    """Validate that all required fields have data"""
    required_fields = mapping.get('validation_rules', {}).get('required_fields', [])
    missing_fields = []
    empty_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif not data[field] or data[field].strip() == '':
            empty_fields.append(field)
    
    return missing_fields, empty_fields

def test_field_coverage():
    """Test field coverage across CSV structure"""
    print("🏠 CSV FIELD MAPPING VALIDATION")
    print("=" * 50)
    
    # Load sample data
    csv_data = load_csv_data('sample_offer_data.csv')
    if not csv_data:
        print("❌ Failed to load CSV data")
        return
    
    # Load mapping configuration
    field_mapping = load_field_mapping('comprehensive_field_mapping.json')
    if not field_mapping:
        print("❌ Failed to load field mapping")
        return
    
    print(f"✅ Loaded CSV with {len(csv_data)} fields")
    print(f"✅ Loaded mapping configuration")
    
    # Validate required fields
    missing, empty = validate_required_fields(csv_data, field_mapping)
    
    print(f"\n📊 VALIDATION RESULTS:")
    print(f"   Total CSV fields: {len(csv_data)}")
    print(f"   Expected fields: {field_mapping['csv_structure']['total_fields']}")
    print(f"   Missing required fields: {len(missing)}")
    print(f"   Empty required fields: {len(empty)}")
    
    if missing:
        print(f"\n❌ Missing required fields:")
        for field in missing:
            print(f"   - {field}")
    
    if empty:
        print(f"\n⚠️  Empty required fields:")
        for field in empty:
            print(f"   - {field}")
    
    # Test field categories
    print(f"\n📋 FIELD CATEGORY BREAKDOWN:")
    categories = field_mapping['csv_structure']['categories']
    for category, info in categories.items():
        expected_count = info['count']
        actual_fields = [f for f in info['fields'] if f in csv_data]
        filled_fields = [f for f in actual_fields if csv_data[f] and csv_data[f].strip()]
        
        print(f"   {category}: {len(filled_fields)}/{expected_count} fields populated")
    
    # Test specific form mappings
    print(f"\n🔍 FORM MAPPING VALIDATION:")
    form_mappings = field_mapping['form_field_mappings']
    for form_name, form_info in form_mappings.items():
        primary_fields = form_info.get('primary_fields', {})
        mapped_fields = [f for f in primary_fields.keys() if f in csv_data and csv_data[f]]
        
        print(f"   {form_name}: {len(mapped_fields)}/{len(primary_fields)} primary fields available")
    
    # Create summary
    total_populated = len([f for f in csv_data.values() if f and f.strip()])
    completion_rate = (total_populated / len(csv_data)) * 100
    
    print(f"\n🎯 COMPLETION SUMMARY:")
    print(f"   Data completion rate: {completion_rate:.1f}%")
    print(f"   Ready for form generation: {'✅ YES' if not missing and not empty else '❌ NO'}")
    
    # Test timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"   Validation timestamp: {timestamp}")
    
    return not missing and not empty

if __name__ == "__main__":
    success = test_field_coverage()
    exit(0 if success else 1)