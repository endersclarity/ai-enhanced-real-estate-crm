#!/usr/bin/env python3
"""
Clear all filled form fields from a PDF to create a blank template.
This script preserves the form structure while clearing all field values.
"""

import os
import sys
from PyPDF2 import PdfReader, PdfWriter

def clear_pdf_fields(input_path, output_path):
    """
    Clear all form field values from a PDF while preserving the form structure.
    
    Args:
        input_path (str): Path to the source PDF with filled fields
        output_path (str): Path where the blank template will be saved
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the source PDF
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Copy all pages to the writer
        for page in reader.pages:
            writer.add_page(page)
        
        # Clear form fields if they exist
        if reader.trailer.get('/AcroForm'):
            print(f"📝 Found interactive form fields in PDF")
            
            # Get form fields
            if hasattr(writer, '_flatten'):
                # For newer PyPDF2 versions, we need to handle fields differently
                fields = reader.get_form_text_fields()
                if fields:
                    print(f"🔍 Found {len(fields)} form fields:")
                    for field_name, field_value in fields.items():
                        print(f"   - {field_name}: '{field_value}'")
                
                # Clear all field values by updating them to empty strings
                if hasattr(writer, 'update_page_form_field_values'):
                    for page_num in range(len(writer.pages)):
                        blank_fields = {name: '' for name in fields.keys()}
                        writer.update_page_form_field_values(writer.pages[page_num], blank_fields)
                        print(f"✅ Cleared fields on page {page_num + 1}")
            
            # Alternative method: Clone fields and clear values
            elif '/AcroForm' in reader.trailer and '/Fields' in reader.trailer['/AcroForm']:
                print("🔄 Using alternative field clearing method...")
                # Copy the AcroForm but with cleared field values
                writer.clone_reader_document_root(reader)
        else:
            print("ℹ️  No interactive form fields found - this may be a static PDF")
        
        # Write the cleared PDF to output
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        print(f"✅ Successfully created blank template: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing PDF fields: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False

def main():
    """Main function to clear PDF fields"""
    source_file = "/home/ender/.claude/projects/offer-creator/California_Residential_Purchase_Agreement_-_1224_ts77432.pdf"
    output_file = "/home/ender/.claude/projects/offer-creator/California_Residential_Purchase_Agreement_BLANK_TEMPLATE.pdf"
    
    # Check if source file exists
    if not os.path.exists(source_file):
        print(f"❌ Source file not found: {source_file}")
        return False
    
    print(f"🎯 Clearing form fields from: {source_file}")
    print(f"💾 Creating blank template: {output_file}")
    
    # Clear the fields
    success = clear_pdf_fields(source_file, output_file)
    
    if success:
        # Verify the output file was created
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"📄 Blank template created successfully ({file_size:,} bytes)")
            
            # Compare file sizes
            original_size = os.path.getsize(source_file)
            print(f"📊 Original: {original_size:,} bytes → Blank: {file_size:,} bytes")
            
            return True
        else:
            print(f"❌ Output file was not created: {output_file}")
            return False
    else:
        print(f"❌ Failed to clear PDF fields")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)