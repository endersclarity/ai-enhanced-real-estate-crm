#!/usr/bin/env python3
"""
Simple test to see what's actually in this PDF
"""

import fitz  # PyMuPDF

pdf_path = "California_RPA_Template_Fillable.pdf"

print("🔍 SIMPLE PDF INSPECTION")
print("=" * 40)

try:
    doc = fitz.open(pdf_path)
    print(f"Pages: {len(doc)}")
    
    # Check first page for form fields
    page = doc[0]
    widgets = list(page.widgets())
    
    print(f"Form widgets on page 1: {len(widgets)}")
    
    if widgets:
        print("\nFirst 10 fields:")
        for i, widget in enumerate(widgets[:10]):
            print(f"  {i+1}. Name: '{widget.field_name}'")
            print(f"     Type: {widget.field_type}")
            print(f"     Current value: '{widget.field_value}'")
            
            # Try to fill this field
            if widget.field_name:
                widget.field_value = f"TEST_{i+1}"
                widget.update()
                
    # Save a test version
    doc.save("TEST_FILLED.pdf")
    doc.close()
    
    print(f"\n✅ Saved test file: TEST_FILLED.pdf")
    print("Check if this one has visible text!")
    
except Exception as e:
    print(f"Error: {e}")