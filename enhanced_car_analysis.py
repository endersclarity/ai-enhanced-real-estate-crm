#!/usr/bin/env python3
"""
Enhanced CAR Forms Analysis
Handles encrypted PDFs and text-based field detection
"""

import os
import json
import re
from pathlib import Path
import pdfplumber
from collections import defaultdict

def extract_text_fields_from_pdf(pdf_path):
    """Extract text and identify potential form fields through pattern recognition"""
    field_patterns = []
    text_blocks = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_text = ""
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"
                    
                    # Extract words with coordinates for potential field mapping
                    try:
                        words = page.extract_words()
                        for word in words:
                            if 'x0' in word:
                                text_blocks.append({
                                    'text': word['text'],
                                    'x0': round(word['x0'], 2),
                                    'y0': round(word['y0'], 2),
                                    'page': page_num
                                })
                    except:
                        pass  # Skip if word extraction fails
            
            # Pattern matching for common form fields
            field_patterns = identify_form_patterns(all_text)
            
    except Exception as e:
        print(f"❌ Enhanced analysis error for {pdf_path}: {e}")
    
    return {
        'text_blocks': text_blocks[:50],  # Limit for analysis
        'field_patterns': field_patterns,
        'total_text_length': len(all_text) if 'all_text' in locals() else 0
    }

def identify_form_patterns(text):
    """Identify potential form fields through text pattern recognition"""
    patterns = {
        'dates': [],
        'names': [],
        'addresses': [],
        'phone_numbers': [],
        'email_addresses': [],
        'monetary_amounts': [],
        'checkboxes': [],
        'signature_lines': [],
        'property_info': [],
        'legal_descriptions': []
    }
    
    # Date patterns
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
        r'Date:?\s*[_\s]{5,}',
        r'Dated:?\s*[_\s]{5,}'
    ]
    
    # Name patterns
    name_patterns = [
        r'Name:?\s*[_\s]{10,}',
        r'Buyer:?\s*[_\s]{10,}',
        r'Seller:?\s*[_\s]{10,}',
        r'Agent:?\s*[_\s]{10,}',
        r'Client:?\s*[_\s]{10,}'
    ]
    
    # Address patterns
    address_patterns = [
        r'Address:?\s*[_\s]{10,}',
        r'Property Address:?\s*[_\s]{10,}',
        r'Street:?\s*[_\s]{10,}',
        r'City:?\s*[_\s]{10,}',
        r'State:?\s*[_\s]{5,}',
        r'ZIP:?\s*[_\s]{5,}'
    ]
    
    # Phone patterns
    phone_patterns = [
        r'Phone:?\s*[_\s]{10,}',
        r'Cell:?\s*[_\s]{10,}',
        r'Tel:?\s*[_\s]{10,}',
        r'\(\s*\)\s*[_\s]{5,}'
    ]
    
    # Email patterns
    email_patterns = [
        r'Email:?\s*[_\s]{10,}',
        r'E-mail:?\s*[_\s]{10,}'
    ]
    
    # Monetary patterns
    money_patterns = [
        r'\$\s*[_\s]{5,}',
        r'Price:?\s*\$?\s*[_\s]{5,}',
        r'Amount:?\s*\$?\s*[_\s]{5,}',
        r'Commission:?\s*[_\s]{5,}'
    ]
    
    # Checkbox patterns
    checkbox_patterns = [
        r'☐\s*[A-Za-z]',
        r'□\s*[A-Za-z]',
        r'\[\s*\]\s*[A-Za-z]',
        r'YES\s*☐\s*NO\s*☐',
        r'Yes\s*☐\s*No\s*☐'
    ]
    
    # Signature patterns
    signature_patterns = [
        r'Signature:?\s*[_\s]{10,}',
        r'Sign:?\s*[_\s]{10,}',
        r'X[_\s]{10,}',
        r'Buyer\'s Signature:?\s*[_\s]{10,}',
        r'Seller\'s Signature:?\s*[_\s]{10,}'
    ]
    
    # Property information patterns
    property_patterns = [
        r'APN:?\s*[_\s]{10,}',
        r'Parcel:?\s*[_\s]{10,}',
        r'MLS:?\s*[_\s]{10,}',
        r'Square Feet:?\s*[_\s]{10,}',
        r'Bedrooms:?\s*[_\s]{5,}',
        r'Bathrooms:?\s*[_\s]{5,}'
    ]
    
    # Legal description patterns
    legal_patterns = [
        r'Legal Description:?\s*[_\s]{10,}',
        r'Lot:?\s*[_\s]{10,}',
        r'Block:?\s*[_\s]{10,}',
        r'Tract:?\s*[_\s]{10,}'
    ]
    
    # Apply all patterns
    pattern_groups = [
        ('dates', date_patterns),
        ('names', name_patterns),
        ('addresses', address_patterns),
        ('phone_numbers', phone_patterns),
        ('email_addresses', email_patterns),
        ('monetary_amounts', money_patterns),
        ('checkboxes', checkbox_patterns),
        ('signature_lines', signature_patterns),
        ('property_info', property_patterns),
        ('legal_descriptions', legal_patterns)
    ]
    
    for category, pattern_list in pattern_groups:
        for pattern in pattern_list:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                patterns[category].append({
                    'pattern': pattern,
                    'match': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
    
    return patterns

def analyze_california_purchase_agreement():
    """Special analysis for the main California Residential Purchase Agreement"""
    pdf_path = 'car_forms/California_Residential_Purchase_Agreement_-_1224_ts77432.pdf'
    
    print("\n🏠 SPECIAL ANALYSIS: California Residential Purchase Agreement")
    print("=" * 60)
    
    analysis = extract_text_fields_from_pdf(pdf_path)
    
    # Count pattern types
    pattern_counts = {}
    for category, patterns in analysis['field_patterns'].items():
        pattern_counts[category] = len(patterns)
    
    print(f"📄 Text Length: {analysis['total_text_length']} characters")
    print(f"📝 Text Blocks Extracted: {len(analysis['text_blocks'])}")
    
    print("\n🔍 Field Patterns Detected:")
    for category, count in pattern_counts.items():
        if count > 0:
            print(f"   {category.replace('_', ' ').title()}: {count}")
    
    # Show sample patterns
    for category, patterns in analysis['field_patterns'].items():
        if patterns and len(patterns) > 0:
            print(f"\n📋 Sample {category.replace('_', ' ').title()}:")
            for pattern in patterns[:3]:  # Show first 3
                print(f"   - {pattern['match']}")
    
    return analysis

def create_field_mapping_template():
    """Create template for CRM-to-form field mapping (Task #3 prep)"""
    
    # Based on the existing CRM schema (177 fields)
    crm_field_categories = {
        'client_info': [
            'first_name', 'last_name', 'email', 'phone', 'address',
            'city', 'state', 'zip', 'date_of_birth', 'ssn'
        ],
        'property_info': [
            'property_address', 'property_city', 'property_state', 'property_zip',
            'apn', 'mls_number', 'square_feet', 'bedrooms', 'bathrooms',
            'lot_size', 'year_built', 'property_type'
        ],
        'transaction_info': [
            'purchase_price', 'earnest_money', 'closing_date', 'possession_date',
            'loan_amount', 'down_payment', 'commission_rate', 'listing_agent',
            'selling_agent', 'escrow_company', 'title_company'
        ],
        'legal_info': [
            'legal_description', 'parcel_number', 'deed_restrictions',
            'hoa_fees', 'property_taxes', 'special_assessments'
        ]
    }
    
    mapping_template = {
        'form_name': 'California_Residential_Purchase_Agreement',
        'crm_to_form_mappings': {},
        'validation_rules': {},
        'default_values': {},
        'conditional_mappings': {}
    }
    
    # Create placeholder mappings
    for category, fields in crm_field_categories.items():
        for field in fields:
            mapping_template['crm_to_form_mappings'][field] = {
                'form_field_id': f'auto_detected_{field}',
                'field_type': 'text',
                'coordinates': {'x': 0, 'y': 0, 'page': 1},
                'required': False,
                'category': category
            }
    
    return mapping_template

def main():
    print("🚀 Enhanced CAR Forms Analysis")
    print("🔍 Pattern-based field detection for encrypted PDFs")
    print("=" * 60)
    
    # Special focus on main purchase agreement (27 pages)
    purchase_agreement_analysis = analyze_california_purchase_agreement()
    
    # Create field mapping template for Task #3
    mapping_template = create_field_mapping_template()
    
    # Save results
    results = {
        'california_purchase_agreement_analysis': purchase_agreement_analysis,
        'field_mapping_template': mapping_template,
        'analysis_method': 'pattern_recognition',
        'timestamp': '2025-06-01T06:45:00Z'
    }
    
    with open('enhanced_car_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Enhanced analysis saved to: enhanced_car_analysis.json")
    print("🎯 Focus: California Residential Purchase Agreement (27 pages)")
    print("📋 Field mapping template prepared for Task #3")
    
    return results

if __name__ == "__main__":
    main()