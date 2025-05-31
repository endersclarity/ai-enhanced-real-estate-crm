#!/usr/bin/env python3

import PyPDF2
import os
import re
from collections import defaultdict

def extract_pdf_text(pdf_path):
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def identify_data_fields(text):
    """Identify potential data fields in the text"""
    fields = []
    
    # Pattern for underlines indicating blank fields
    underline_patterns = [
        r'_{3,}',  # 3 or more underscores
        r'_+\s*_+',  # multiple underscore groups
        r'\s_+\s',  # underscores with spaces
    ]
    
    # Pattern for checkboxes
    checkbox_patterns = [
        r'☐',
        r'\[\s*\]',
        r'□',
        r'◻',
    ]
    
    # Date patterns
    date_patterns = [
        r'_+,\s*20_+',
        r'_+/_+/_+',
        r'Date:\s*_+',
        r'__/__/__',
        r'_+,\s*_+',
    ]
    
    # Common field labels
    field_labels = [
        r'Buyer(?:\(s\))?\s*:?\s*_+',
        r'Seller(?:\(s\))?\s*:?\s*_+',
        r'Property\s+Address\s*:?\s*_+',
        r'Address\s*:?\s*_+',
        r'City\s*:?\s*_+',
        r'State\s*:?\s*_+',
        r'ZIP\s*:?\s*_+',
        r'Price\s*:?\s*\$?\s*_+',
        r'Amount\s*:?\s*\$?\s*_+',
        r'Agent\s*:?\s*_+',
        r'Broker\s*:?\s*_+',
        r'Phone\s*:?\s*_+',
        r'Email\s*:?\s*_+',
        r'License\s*#?\s*:?\s*_+',
        r'APN\s*:?\s*_+',
        r'Loan\s*:?\s*_+',
        r'Down\s+Payment\s*:?\s*_+',
        r'Earnest\s+Money\s*:?\s*_+',
    ]
    
    # Count different types of fields
    for pattern in underline_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            fields.append(('blank_line', match.strip()))
    
    for pattern in checkbox_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            fields.append(('checkbox', match.strip()))
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            fields.append(('date_field', match.strip()))
    
    for pattern in field_labels:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            fields.append(('labeled_field', match.strip()))
    
    return fields

def categorize_fields(text):
    """Categorize types of information based on context"""
    categories = defaultdict(int)
    
    # Buyer information
    buyer_patterns = [
        r'buyer(?:\(s\))?',
        r'purchaser(?:\(s\))?',
        r'client\s+name',
    ]
    
    # Seller information  
    seller_patterns = [
        r'seller(?:\(s\))?',
        r'vendor(?:\(s\))?',
        r'owner(?:\(s\))?',
    ]
    
    # Property details
    property_patterns = [
        r'property\s+address',
        r'real\s+property',
        r'premises',
        r'lot\s+size',
        r'square\s+feet',
        r'bedrooms?',
        r'bathrooms?',
        r'garage',
        r'apn',
        r'assessor',
    ]
    
    # Financial data
    financial_patterns = [
        r'purchase\s+price',
        r'sale\s+price',
        r'down\s+payment',
        r'earnest\s+money',
        r'deposit',
        r'loan\s+amount',
        r'financing',
        r'interest\s+rate',
        r'commission',
        r'fee(?:s)?',
        r'\$',
    ]
    
    # Agent/Broker information
    agent_patterns = [
        r'agent',
        r'broker',
        r'realtor',
        r'license',
        r'dre\s*#?',
        r'phone',
        r'email',
        r'office',
    ]
    
    # Dates and deadlines
    date_patterns = [
        r'date',
        r'deadline',
        r'expir',
        r'close\s+of\s+escrow',
        r'contingency',
        r'inspection',
        r'appraisal',
    ]
    
    # Count occurrences in each category
    text_lower = text.lower()
    
    for pattern in buyer_patterns:
        categories['buyer_info'] += len(re.findall(pattern, text_lower))
    
    for pattern in seller_patterns:
        categories['seller_info'] += len(re.findall(pattern, text_lower))
    
    for pattern in property_patterns:
        categories['property_details'] += len(re.findall(pattern, text_lower))
    
    for pattern in financial_patterns:
        categories['financial_data'] += len(re.findall(pattern, text_lower))
    
    for pattern in agent_patterns:
        categories['agent_broker_info'] += len(re.findall(pattern, text_lower))
    
    for pattern in date_patterns:
        categories['dates_deadlines'] += len(re.findall(pattern, text_lower))
    
    return categories

def main():
    forms_dir = "/home/ender/.claude/projects/offer-creator/forms"
    
    all_fields = []
    all_categories = defaultdict(int)
    form_analysis = {}
    
    print("CALIFORNIA REAL ESTATE FORMS ANALYSIS")
    print("=" * 50)
    
    # Process each PDF
    for filename in sorted(os.listdir(forms_dir)):
        if filename.endswith('.pdf'):
            print(f"\nAnalyzing: {filename}")
            pdf_path = os.path.join(forms_dir, filename)
            
            text = extract_pdf_text(pdf_path)
            if not text:
                continue
                
            fields = identify_data_fields(text)
            categories = categorize_fields(text)
            
            # Store analysis
            form_analysis[filename] = {
                'text_length': len(text),
                'total_fields': len(fields),
                'categories': dict(categories)
            }
            
            # Aggregate data
            all_fields.extend(fields)
            for cat, count in categories.items():
                all_categories[cat] += count
            
            print(f"  Text length: {len(text)} characters")
            print(f"  Identified fields: {len(fields)}")
            print(f"  Categories: {dict(categories)}")
    
    print("\n" + "=" * 50)
    print("SUMMARY ANALYSIS")
    print("=" * 50)
    
    # Field type summary
    field_types = defaultdict(int)
    for field_type, _ in all_fields:
        field_types[field_type] += 1
    
    print(f"\nField Types Identified:")
    for field_type, count in sorted(field_types.items()):
        print(f"  {field_type}: {count}")
    
    print(f"\nCategory Distribution:")
    for category, count in sorted(all_categories.items()):
        print(f"  {category}: {count}")
    
    print(f"\nTotal forms analyzed: {len(form_analysis)}")
    print(f"Total fields identified: {len(all_fields)}")
    
    # Estimate CSV columns needed
    estimated_columns = estimate_csv_columns(all_categories, field_types)
    print(f"\nEstimated CSV columns needed: {estimated_columns}")
    
    return form_analysis, all_fields, all_categories

def estimate_csv_columns(categories, field_types):
    """Estimate number of CSV columns needed"""
    
    # Base person information (repeated for buyer/seller/agents)
    person_fields = [
        'first_name', 'last_name', 'middle_initial', 
        'address', 'city', 'state', 'zip_code',
        'phone', 'email', 'signature', 'date_signed'
    ]
    
    # Property information
    property_fields = [
        'property_address', 'property_city', 'property_state', 'property_zip',
        'apn', 'lot_size', 'square_footage', 'bedrooms', 'bathrooms',
        'property_type', 'year_built', 'garage_spaces'
    ]
    
    # Financial information
    financial_fields = [
        'purchase_price', 'down_payment', 'loan_amount', 'earnest_money',
        'closing_costs', 'commission_rate', 'commission_amount',
        'inspection_costs', 'appraisal_costs', 'title_insurance'
    ]
    
    # Date information
    date_fields = [
        'offer_date', 'acceptance_date', 'close_of_escrow_date',
        'inspection_deadline', 'appraisal_deadline', 'loan_approval_deadline',
        'contingency_removal_date'
    ]
    
    # Checkbox/boolean fields
    checkbox_fields = [
        'cash_offer', 'financing_contingency', 'inspection_contingency',
        'appraisal_contingency', 'sale_of_property_contingency',
        'as_is_condition', 'seller_financing'
    ]
    
    # Agent/Broker information (buyer and listing agents)
    agent_fields = [
        'buyer_agent_name', 'buyer_agent_license', 'buyer_agent_phone',
        'buyer_agent_email', 'buyer_broker_name', 'buyer_broker_license',
        'listing_agent_name', 'listing_agent_license', 'listing_agent_phone',
        'listing_agent_email', 'listing_broker_name', 'listing_broker_license'
    ]
    
    # Calculate totals
    buyer_seller_fields = len(person_fields) * 2  # Buyer and Seller
    
    total_estimated = (
        buyer_seller_fields +
        len(property_fields) +
        len(financial_fields) +
        len(date_fields) +
        len(checkbox_fields) +
        len(agent_fields) +
        20  # Additional miscellaneous fields
    )
    
    return total_estimated

if __name__ == "__main__":
    main()