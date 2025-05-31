#!/usr/bin/env python3
"""
Test script to analyze and fill the downloaded California RPA template
"""

import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import BooleanObject, NameObject, IndirectObject
import os

def analyze_pdf_fields(pdf_path):
    """Analyze PDF form fields"""
    print(f"Analyzing PDF: {pdf_path}")
    
    try:
        reader = PdfReader(pdf_path)
        
        if reader.is_encrypted:
            print("PDF is encrypted!")
            return None
            
        print(f"Number of pages: {len(reader.pages)}")
        
        # Check for form fields
        if "/AcroForm" in reader.trailer["/Root"]:
            acro_form = reader.trailer["/Root"]["/AcroForm"]
            if "/Fields" in acro_form:
                fields = acro_form["/Fields"]
                print(f"\nFound {len(fields)} form fields:")
                
                field_names = []
                for field in fields:
                    field_obj = field.get_object()
                    if "/T" in field_obj:
                        field_name = field_obj["/T"]
                        field_type = field_obj.get("/FT", "Unknown")
                        print(f"  - {field_name} (Type: {field_type})")
                        field_names.append(field_name)
                
                return field_names
            else:
                print("No form fields found in AcroForm")
        else:
            print("No AcroForm found - this might not be a fillable PDF")
            
        return []
        
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        return None

def fill_pdf_with_dummy_data(input_pdf, output_pdf):
    """Fill PDF with dummy real estate data"""
    
    # Dummy real estate data
    dummy_data = {
        'buyer_name': 'John Doe',
        'buyer_address': '123 Main St, Los Angeles, CA 90210',
        'seller_name': 'Jane Smith', 
        'seller_address': '456 Oak Ave, Beverly Hills, CA 90210',
        'property_address': '789 Elm Street, Santa Monica, CA 90401',
        'purchase_price': '$750,000',
        'deposit_amount': '$25,000',
        'closing_date': '2025-07-15',
        'agent_name': 'Narissa Realty Agent',
        'agent_phone': '(310) 555-0123',
        'agent_email': 'agent@narissarealty.com'
    }
    
    try:
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        # Try to fill fields if they exist
        if "/AcroForm" in reader.trailer["/Root"]:
            writer.update_page_form_field_values(
                writer.pages[0], dummy_data
            )
            
        # Write the filled PDF
        with open(output_pdf, 'wb') as output_file:
            writer.write(output_file)
            
        print(f"✅ Successfully created filled PDF: {output_pdf}")
        print("📋 Used dummy data:")
        for key, value in dummy_data.items():
            print(f"  {key}: {value}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error filling PDF: {e}")
        return False

def main():
    pdf_file = "California_RPA_Template_Fillable.pdf"
    output_file = "California_RPA_FILLED_TEST.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"PDF file not found: {pdf_file}")
        return
        
    print("🏠 CALIFORNIA RESIDENTIAL PURCHASE AGREEMENT - FILLABLE TEST")
    print("=" * 60)
    
    # Analyze the PDF structure
    field_names = analyze_pdf_fields(pdf_file)
    
    print("\n" + "=" * 60)
    
    # Try to fill it with dummy data
    if fill_pdf_with_dummy_data(pdf_file, output_file):
        print(f"\n🎯 PROOF OF CONCEPT COMPLETE!")
        print(f"   Original: {pdf_file}")
        print(f"   Filled:   {output_file}")
        print(f"   Ready for testing!")
    else:
        print(f"\n❌ Failed to fill PDF")

if __name__ == "__main__":
    main()