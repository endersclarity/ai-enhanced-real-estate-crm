#!/usr/bin/env python3
"""
Debug script to understand why PDF form filling isn't working
"""

import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import fitz  # PyMuPDF
import sys

def debug_with_pymupdf(pdf_path):
    """Use PyMuPDF to inspect and fill form fields"""
    print("=" * 60)
    print("DEBUGGING WITH PyMuPDF (fitz)")
    print("=" * 60)
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            if widgets:
                print(f"Page {page_num + 1} has {len(widgets)} form widgets:")
                for widget in widgets:
                    print(f"  Field: {widget.field_name}")
                    print(f"  Type: {widget.field_type}")
                    print(f"  Value: {widget.field_value}")
                    print(f"  Rect: {widget.rect}")
                    print("  ---")
            else:
                print(f"Page {page_num + 1}: No form widgets found")
                
        doc.close()
        return True
        
    except Exception as e:
        print(f"PyMuPDF error: {e}")
        return False

def fill_with_pymupdf(input_pdf, output_pdf):
    """Try filling with PyMuPDF"""
    print("\nTrying to fill with PyMuPDF...")
    
    try:
        doc = fitz.open(input_pdf)
        
        # Sample data
        fill_data = {
            'Buyer': 'John Doe - PyMuPDF Test',
            'Seller': 'Jane Smith - PyMuPDF Test',
            'Property address and the legal description': '789 Test Street, CA'
        }
        
        filled_any = False
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                field_name = widget.field_name
                if field_name in fill_data:
                    widget.field_value = fill_data[field_name]
                    widget.update()
                    filled_any = True
                    print(f"✅ Filled field: {field_name}")
                    
        if filled_any:
            doc.save(output_pdf)
            print(f"✅ Saved filled PDF: {output_pdf}")
        else:
            print("❌ No fields were filled")
            
        doc.close()
        return filled_any
        
    except Exception as e:
        print(f"❌ PyMuPDF fill error: {e}")
        return False

def main():
    pdf_file = "California_RPA_Template_Fillable.pdf"
    
    print("🔍 PDF FORM FIELD DEBUGGING")
    print("Investigating why form filling isn't working...")
    
    # First debug with PyMuPDF
    if debug_with_pymupdf(pdf_file):
        # Try filling with PyMuPDF
        output_file = "California_RPA_PYMUPDF_FILLED.pdf"
        if fill_with_pymupdf(pdf_file, output_file):
            print(f"\n🎯 SUCCESS! Created: {output_file}")
        else:
            print(f"\n❌ PyMuPDF filling also failed")
    
if __name__ == "__main__":
    main()