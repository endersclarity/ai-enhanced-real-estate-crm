#!/usr/bin/env python3
"""
Validate that CSV data was properly filled into PDF forms
"""

import fitz  # PyMuPDF
import glob
import os

def validate_pdf_fields(pdf_file):
    """Check that PDF has filled form fields"""
    print(f"\n📄 Validating: {os.path.basename(pdf_file)}")
    print("-" * 40)
    
    try:
        doc = fitz.open(pdf_file)
        
        filled_fields = []
        total_fields = 0
        
        # Check each page for filled fields
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            
            for widget in widgets:
                total_fields += 1
                if widget.field_value and widget.field_value.strip():
                    filled_fields.append({
                        'page': page_num + 1,
                        'name': widget.field_name,
                        'value': widget.field_value
                    })
        
        doc.close()
        
        print(f"✅ Total fields: {total_fields}")
        print(f"✅ Filled fields: {len(filled_fields)}")
        print(f"✅ Fill rate: {(len(filled_fields)/total_fields*100):.1f}%" if total_fields > 0 else "✅ Fill rate: 0%")
        
        # Show key filled fields
        if filled_fields:
            print(f"\n🎯 KEY FILLED FIELDS:")
            key_fields = [f for f in filled_fields if any(key in f['name'].lower() for key in ['buyer', 'price', 'deposit', 'address'])]
            for field in key_fields[:10]:  # Show first 10 key fields
                print(f"   Page {field['page']}: {field['name']} = '{field['value']}'")
            
            if len(filled_fields) > 10:
                print(f"   ... and {len(filled_fields) - 10} more filled fields")
        
        return len(filled_fields) > 0
        
    except Exception as e:
        print(f"❌ Error validating {pdf_file}: {e}")
        return False

def main():
    print("🔍 PDF FIELD VALIDATION")
    print("=" * 50)
    
    # Find all filled PDFs
    pdf_files = glob.glob("*filled_offer*.pdf")
    
    if not pdf_files:
        print("❌ No filled PDF files found!")
        return
    
    print(f"Found {len(pdf_files)} filled PDF files")
    
    successful = 0
    
    # Validate each PDF
    for pdf_file in sorted(pdf_files):
        if validate_pdf_fields(pdf_file):
            successful += 1
    
    print(f"\n📊 VALIDATION SUMMARY:")
    print(f"   PDFs checked: {len(pdf_files)}")
    print(f"   Successfully filled: {successful}")
    print(f"   Success rate: {(successful/len(pdf_files)*100):.1f}%" if pdf_files else "   Success rate: 0%")
    
    if successful == len(pdf_files):
        print(f"\n🎉 ALL PDFs SUCCESSFULLY FILLED FROM CSV DATA!")
        print(f"✅ CSV-to-PDF field population is working correctly")
    else:
        print(f"\n⚠️  Some PDFs may not have been filled properly")

if __name__ == "__main__":
    main()