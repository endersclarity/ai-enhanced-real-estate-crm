#!/usr/bin/env python3

import os
from PyPDF2 import PdfReader
import json
from collections import defaultdict

def analyze_pdf_fields(pdf_path):
    """Extract all fillable fields from a PDF"""
    try:
        reader = PdfReader(pdf_path)
        fields = reader.get_fields()
        
        if not fields:
            return {}
            
        field_info = {}
        for field_name, field_obj in fields.items():
            field_info[field_name] = {
                'type': field_obj.get('/FT', 'Unknown'),
                'value': field_obj.get('/V', ''),
                'default': field_obj.get('/DV', ''),
                'max_length': field_obj.get('/MaxLen', None)
            }
        
        return field_info
    except Exception as e:
        print(f"Error analyzing {pdf_path}: {e}")
        return {}

def analyze_all_forms():
    """Analyze all forms in the forms directory"""
    forms_dir = "forms"
    all_fields = {}
    field_frequency = defaultdict(int)
    field_patterns = defaultdict(list)
    
    # Get all PDF files
    pdf_files = [f for f in os.listdir(forms_dir) if f.endswith('.pdf')]
    
    print(f"📊 Analyzing {len(pdf_files)} California Real Estate Forms...")
    print("=" * 60)
    
    for pdf_file in sorted(pdf_files):
        pdf_path = os.path.join(forms_dir, pdf_file)
        form_name = pdf_file.replace('.pdf', '').split('_-_')[0]
        
        print(f"\n🔍 {form_name}")
        fields = analyze_pdf_fields(pdf_path)
        
        if fields:
            all_fields[form_name] = fields
            print(f"   Found {len(fields)} fillable fields")
            
            # Track field patterns
            for field_name in fields.keys():
                field_frequency[field_name] += 1
                field_patterns[field_name.lower()].append((form_name, field_name))
        else:
            print(f"   ❌ No fillable fields found")
    
    return all_fields, field_frequency, field_patterns

def categorize_fields(field_patterns):
    """Categorize fields by likely content type"""
    categories = {
        'buyer_info': [],
        'seller_info': [],
        'property_info': [],
        'agent_info': [],
        'financial_info': [],
        'dates': [],
        'signatures': [],
        'checkboxes': [],
        'other': []
    }
    
    buyer_keywords = ['buyer', 'purchaser', 'client']
    seller_keywords = ['seller', 'owner', 'vendor'] 
    property_keywords = ['property', 'address', 'apn', 'lot', 'county', 'zip']
    agent_keywords = ['agent', 'broker', 'realtor', 'license']
    financial_keywords = ['price', 'loan', 'down', 'deposit', 'commission', 'fee', 'cost']
    date_keywords = ['date', 'deadline', 'expir', 'close', 'closing']
    signature_keywords = ['sign', 'initial', 'print name']
    
    for field_lower, instances in field_patterns.items():
        field_name = instances[0][1]  # Use actual field name from first instance
        
        if any(kw in field_lower for kw in buyer_keywords):
            categories['buyer_info'].append(field_name)
        elif any(kw in field_lower for kw in seller_keywords):
            categories['seller_info'].append(field_name)
        elif any(kw in field_lower for kw in property_keywords):
            categories['property_info'].append(field_name)
        elif any(kw in field_lower for kw in agent_keywords):
            categories['agent_info'].append(field_name)
        elif any(kw in field_lower for kw in financial_keywords):
            categories['financial_info'].append(field_name)
        elif any(kw in field_lower for kw in date_keywords):
            categories['dates'].append(field_name)
        elif any(kw in field_lower for kw in signature_keywords):
            categories['signatures'].append(field_name)
        elif 'check' in field_lower or 'box' in field_lower:
            categories['checkboxes'].append(field_name)
        else:
            categories['other'].append(field_name)
    
    return categories

def main():
    print("🏠 CALIFORNIA REAL ESTATE FORMS ANALYSIS")
    print("=" * 50)
    
    all_fields, field_frequency, field_patterns = analyze_all_forms()
    
    # Summary statistics
    total_unique_fields = len(field_patterns)
    total_field_instances = sum(field_frequency.values())
    
    print(f"\n📊 SUMMARY STATISTICS:")
    print(f"   Forms analyzed: {len(all_fields)}")
    print(f"   Total unique field names: {total_unique_fields}")
    print(f"   Total field instances: {total_field_instances}")
    print(f"   Average fields per form: {total_field_instances/len(all_fields):.1f}")
    
    # Categorize fields
    categories = categorize_fields(field_patterns)
    
    print(f"\n🏷️  FIELD CATEGORIES:")
    for category, fields in categories.items():
        if fields:
            print(f"   {category.replace('_', ' ').title()}: {len(fields)} fields")
    
    # Show most common fields (appear in multiple forms)
    common_fields = {k: v for k, v in field_frequency.items() if v > 1}
    if common_fields:
        print(f"\n🔄 COMMON FIELDS (appear in multiple forms):")
        for field, count in sorted(common_fields.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {field}: {count} forms")
    
    # Save detailed analysis
    analysis_data = {
        'summary': {
            'forms_count': len(all_fields),
            'unique_fields': total_unique_fields,
            'total_instances': total_field_instances
        },
        'categories': categories,
        'field_frequency': dict(field_frequency),
        'all_fields': all_fields
    }
    
    with open('forms_analysis.json', 'w') as f:
        json.dump(analysis_data, f, indent=2)
    
    print(f"\n💾 Detailed analysis saved to forms_analysis.json")
    print(f"\n🎯 MASTER CSV ANSWER: You would need {total_unique_fields} columns")

if __name__ == "__main__":
    main()