#!/usr/bin/env python3
import PyPDF2
import os
import re
from collections import defaultdict, Counter

def extract_pdf_text(pdf_path):
    """Extract text from a PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return f"Error reading {pdf_path}: {str(e)}"

def extract_specific_fields(text, filename):
    """Extract specific real estate form fields"""
    
    fields = {}
    
    # Property address patterns
    property_patterns = [
        r'Property Address[:\s]+([^\n]+)',
        r'Subject Property[:\s]+([^\n]+)',
        r'Property[:\s]+([^\n]+)',
        r'(\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Circle|Cir|Court|Ct)[^\n,]*)',
    ]
    
    # Price patterns
    price_patterns = [
        r'Purchase Price[:\s]+\$?([\d,]+\.?\d*)',
        r'Sale Price[:\s]+\$?([\d,]+\.?\d*)',
        r'Listing Price[:\s]+\$?([\d,]+\.?\d*)',
        r'\$(\d{3,}(?:,\d{3})*(?:\.\d{2})?)',
    ]
    
    # Date patterns
    date_patterns = [
        r'Date[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})',
        r'Closing Date[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})',
        r'Contract Date[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})',
        r'(\d{1,2}/\d{1,2}/\d{2,4})',
    ]
    
    # Names patterns
    name_patterns = [
        r'Buyer[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'Seller[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'Agent[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'([A-Z][a-z]+\s+[A-Z][a-z]+)',
    ]
    
    # Contact info patterns
    contact_patterns = [
        r'Phone[:\s]*(\(\d{3}\)\s*\d{3}-\d{4})',
        r'Email[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
        r'(\(\d{3}\)\s*\d{3}-\d{4})',
        r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
    ]
    
    # Extract all matches
    all_properties = []
    all_prices = []
    all_dates = []
    all_names = []
    all_phones = []
    all_emails = []
    
    for pattern in property_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        all_properties.extend(matches)
    
    for pattern in price_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        all_prices.extend(matches)
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        all_dates.extend(matches)
    
    for pattern in name_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        all_names.extend(matches)
    
    for pattern in contact_patterns:
        if 'Phone' in pattern or '(' in pattern:
            matches = re.findall(pattern, text, re.IGNORECASE)
            all_phones.extend(matches)
        else:
            matches = re.findall(pattern, text, re.IGNORECASE)
            all_emails.extend(matches)
    
    # Clean and deduplicate
    fields['properties'] = list(set([p.strip() for p in all_properties if len(p.strip()) > 10]))
    fields['prices'] = list(set([p.replace(',', '') for p in all_prices if p.replace(',', '').replace('.', '').isdigit()]))
    fields['dates'] = list(set([d for d in all_dates if '/' in d]))
    fields['names'] = list(set([n.strip() for n in all_names if len(n.strip()) > 5]))
    fields['phones'] = list(set([p for p in all_phones if '(' in p]))
    fields['emails'] = list(set([e for e in all_emails if '@' in e]))
    
    return fields

def analyze_form_fields():
    """Analyze all forms to identify consistent field patterns"""
    
    forms_dir = "forms"
    all_fields = defaultdict(list)
    form_summaries = []
    
    print("Detailed Field Analysis")
    print("="*50)
    
    for filename in sorted(os.listdir(forms_dir)):
        if filename.endswith('.pdf'):
            filepath = os.path.join(forms_dir, filename)
            text = extract_pdf_text(filepath)
            fields = extract_specific_fields(text, filename)
            
            form_summary = {
                'filename': filename,
                'text_length': len(text),
                'fields': fields
            }
            form_summaries.append(form_summary)
            
            # Add to global collections
            for field_type, values in fields.items():
                all_fields[field_type].extend(values)
            
            print(f"\n{filename}:")
            print(f"  Text length: {len(text):,} chars")
            for field_type, values in fields.items():
                if values:
                    print(f"  {field_type}: {len(values)} items")
                    for value in values[:3]:  # Show first 3
                        print(f"    - {value}")
                    if len(values) > 3:
                        print(f"    ... and {len(values)-3} more")
    
    print("\n" + "="*60)
    print("CONSOLIDATED FIELD ANALYSIS")
    print("="*60)
    
    # Analyze most common values
    for field_type, all_values in all_fields.items():
        unique_values = list(set(all_values))
        value_counts = Counter(all_values)
        
        print(f"\n{field_type.upper()}:")
        print(f"  Total instances: {len(all_values)}")
        print(f"  Unique values: {len(unique_values)}")
        print(f"  Most common:")
        for value, count in value_counts.most_common(5):
            print(f"    {count}x: {value}")
    
    # Estimate practical CSV structure
    print("\n" + "="*60)
    print("PRACTICAL CSV COLUMN RECOMMENDATIONS")
    print("="*60)
    
    recommended_columns = []
    
    # Core property info
    if all_fields['properties']:
        recommended_columns.extend(['property_address', 'property_city', 'property_state', 'property_zip'])
    
    # Financial info
    if all_fields['prices']:
        recommended_columns.extend(['purchase_price', 'listing_price', 'sale_price'])
    
    # Dates
    if all_fields['dates']:
        recommended_columns.extend(['contract_date', 'closing_date', 'listing_date'])
    
    # People
    if all_fields['names']:
        recommended_columns.extend(['buyer_name', 'seller_name', 'listing_agent', 'selling_agent'])
    
    # Contact info
    if all_fields['phones']:
        recommended_columns.extend(['buyer_phone', 'seller_phone', 'agent_phone'])
    
    if all_fields['emails']:
        recommended_columns.extend(['buyer_email', 'seller_email', 'agent_email'])
    
    # Form metadata
    recommended_columns.extend(['form_type', 'form_date', 'transaction_id', 'status'])
    
    print(f"Recommended CSV columns ({len(recommended_columns)}):")
    for i, col in enumerate(recommended_columns, 1):
        print(f"  {i:2d}. {col}")
    
    print(f"\nTotal recommended columns: {len(recommended_columns)}")
    print(f"This covers the actual filled data found across all forms.")
    
    return {
        'form_summaries': form_summaries,
        'all_fields': all_fields,
        'recommended_columns': recommended_columns
    }

if __name__ == "__main__":
    results = analyze_form_fields()