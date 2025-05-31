#!/usr/bin/env python3
import PyPDF2
import os
import re
from collections import defaultdict

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

def analyze_filled_fields(text, filename):
    """Analyze text to identify filled vs empty fields"""
    
    # Remove common template artifacts
    text = re.sub(r'Page \d+ of \d+', '', text)
    text = re.sub(r'Revised \d+/\d+', '', text)
    text = re.sub(r'©.*?CAR.*?FORM', '', text)
    
    filled_data = []
    potential_data = []
    
    # Look for common patterns that indicate filled data
    patterns = {
        'dates': r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
        'money': r'\$[\d,]+\.?\d*',
        'phone': r'\(\d{3}\)\s*\d{3}-\d{4}',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'addresses': r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Circle|Cir|Court|Ct)',
        'names': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Simple name pattern
        'zip_codes': r'\b\d{5}(-\d{4})?\b',
        'times': r'\b\d{1,2}:\d{2}\s*(AM|PM|am|pm)\b',
        'percentages': r'\b\d+\.?\d*%\b',
        'signatures': r'electronically signed|signature|signed'
    }
    
    # Find filled data
    for data_type, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            filled_data.extend([(data_type, match) for match in matches])
    
    # Look for lines that appear to have actual content vs templates
    lines = text.split('\n')
    content_lines = []
    
    for line in lines:
        line = line.strip()
        if len(line) > 10:  # Skip very short lines
            # Skip obvious template text
            if any(skip in line.lower() for skip in [
                'buyer', 'seller', 'agent', 'brokers', 'form', 'page',
                'california association of realtors', 'revised',
                'initial', 'copyright', '©', 'car form',
                'buyer representation agreement', 'purchase agreement'
            ]):
                continue
            
            # Look for lines with actual data
            if any(re.search(pattern, line) for pattern in patterns.values()):
                content_lines.append(line)
    
    return {
        'filename': filename,
        'filled_data': filled_data,
        'content_lines': content_lines,
        'total_text_length': len(text),
        'has_meaningful_content': len(filled_data) > 0 or len(content_lines) > 0
    }

def main():
    forms_dir = "forms"
    results = []
    
    print("Analyzing PDF forms for filled content...\n")
    
    for filename in os.listdir(forms_dir):
        if filename.endswith('.pdf'):
            filepath = os.path.join(forms_dir, filename)
            print(f"Processing: {filename}")
            
            text = extract_pdf_text(filepath)
            analysis = analyze_filled_fields(text, filename)
            results.append(analysis)
            
            # Print immediate results
            print(f"  - Text length: {analysis['total_text_length']} chars")
            print(f"  - Filled data points: {len(analysis['filled_data'])}")
            print(f"  - Content lines: {len(analysis['content_lines'])}")
            print(f"  - Has meaningful content: {analysis['has_meaningful_content']}")
            
            if analysis['filled_data']:
                print("  - Sample filled data:")
                for data_type, value in analysis['filled_data'][:5]:  # Show first 5
                    print(f"    {data_type}: {value}")
            print()
    
    # Summary analysis
    print("\n" + "="*60)
    print("SUMMARY ANALYSIS")
    print("="*60)
    
    total_forms = len(results)
    forms_with_data = sum(1 for r in results if r['has_meaningful_content'])
    
    print(f"Total forms analyzed: {total_forms}")
    print(f"Forms with filled content: {forms_with_data}")
    print(f"Percentage with data: {forms_with_data/total_forms*100:.1f}%")
    
    # Aggregate all filled data types
    all_data_types = defaultdict(list)
    for result in results:
        for data_type, value in result['filled_data']:
            all_data_types[data_type].append(value)
    
    print(f"\nData types found across all forms:")
    for data_type, values in all_data_types.items():
        unique_values = set(values)
        print(f"  {data_type}: {len(unique_values)} unique values")
        if len(unique_values) <= 5:
            print(f"    Examples: {list(unique_values)}")
        else:
            print(f"    Examples: {list(unique_values)[:5]} (+ {len(unique_values)-5} more)")
    
    # Estimate CSV columns needed
    print(f"\nEstimated CSV columns needed:")
    print(f"  - Basic data types found: {len(all_data_types)}")
    print(f"  - Recommended columns: {max(20, len(all_data_types) * 2)}")
    print(f"    (includes variations and metadata for each data type)")

if __name__ == "__main__":
    main()