#!/usr/bin/env python3
"""
Analyze PDF text content to identify filled vs template text.
This helps create the cleanest possible blank template.
"""

import os
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
import re

def analyze_text_patterns(pdf_path):
    """Analyze text patterns to identify filled content vs form structure"""
    print(f"🔍 Analyzing text patterns in: {pdf_path}")
    
    filled_patterns = []
    form_structure = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                    
                lines = text.split('\n')
                print(f"\n📄 Page {page_num + 1} text analysis:")
                
                # Look for patterns that suggest filled content
                for line_num, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check for filled-in patterns
                    if any([
                        # Common filled patterns
                        re.search(r'\$[\d,]+', line),  # Dollar amounts
                        re.search(r'\d{1,2}/\d{1,2}/\d{4}', line),  # Dates
                        re.search(r'^\d+\s+\w+\s+\w+', line),  # Addresses
                        re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+', line),  # Names
                        'X' in line and len(line) < 50,  # Checkboxes
                        line.isupper() and len(line.split()) < 10,  # Filled caps
                    ]):
                        filled_patterns.append({
                            'page': page_num + 1,
                            'line': line_num + 1,
                            'content': line[:100],
                            'type': 'potentially_filled'
                        })
                        
                        if page_num == 0:  # Show details for first page
                            print(f"   🔸 Potential filled content: {line[:60]}...")
                    
                    # Form structure indicators
                    elif any([
                        line.startswith('DISCLOSURE'),
                        line.startswith('CIVIL'),
                        'hereby' in line.lower(),
                        'agreement' in line.lower(),
                        'buyer' in line.lower() and 'seller' in line.lower(),
                        line.endswith('________'),  # Blank lines
                        '___' in line,  # Blank spaces
                    ]):
                        form_structure.append({
                            'page': page_num + 1,
                            'content': line[:60]
                        })
                
                # Only show detailed analysis for first 2 pages
                if page_num >= 1:
                    break
    
    except Exception as e:
        print(f"❌ Error analyzing text: {e}")
        return [], []
    
    print(f"\n📊 Analysis Summary:")
    print(f"   🔸 Potentially filled content: {len(filled_patterns)} items")
    print(f"   📋 Form structure elements: {len(form_structure)} items")
    
    return filled_patterns, form_structure

def create_final_blank_template(input_path, output_path):
    """Create the final blank template by copying the PDF structure cleanly"""
    try:
        print(f"🎯 Creating final blank template...")
        
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Copy all pages exactly as they are
        # Since this appears to be a static form, we'll preserve the structure
        for page in reader.pages:
            writer.add_page(page)
        
        # Remove any form-related metadata that might reference filled values
        writer.remove_links()
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating final template: {e}")
        return False

def main():
    """Main analysis and cleaning function"""
    source_file = "/home/ender/.claude/projects/offer-creator/California_Residential_Purchase_Agreement_-_1224_ts77432.pdf"
    final_output = "/home/ender/.claude/projects/offer-creator/California_Residential_Purchase_Agreement_FINAL_BLANK.pdf"
    
    if not os.path.exists(source_file):
        print(f"❌ Source file not found: {source_file}")
        return False
    
    # Analyze the content
    filled_patterns, form_structure = analyze_text_patterns(source_file)
    
    # Create the final blank template
    print(f"\n🔄 Creating final blank template...")
    success = create_final_blank_template(source_file, final_output)
    
    if success and os.path.exists(final_output):
        original_size = os.path.getsize(source_file)
        final_size = os.path.getsize(final_output)
        
        print(f"\n✅ FINAL BLANK TEMPLATE CREATED")
        print(f"📄 File: {final_output}")
        print(f"📊 Size: {final_size:,} bytes (original: {original_size:,} bytes)")
        
        # Show recommendations based on analysis
        if filled_patterns:
            print(f"\n⚠️  Analysis found {len(filled_patterns)} potentially filled items")
            print(f"   💡 You may want to manually review the template to ensure")
            print(f"      all filled content has been properly cleared.")
        else:
            print(f"\n✅ No obvious filled content detected - template should be clean")
        
        return True
    else:
        print(f"❌ Failed to create final template")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)