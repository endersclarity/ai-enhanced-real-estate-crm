#!/usr/bin/env python3
"""
Advanced PDF cleaner that handles both form fields and annotations.
This attempts multiple methods to create a clean blank template.
"""

import os
import sys
from PyPDF2 import PdfReader, PdfWriter
import pdfplumber

def analyze_pdf_structure(pdf_path):
    """Analyze PDF structure to understand what needs to be cleaned"""
    print(f"🔍 Analyzing PDF structure: {pdf_path}")
    
    try:
        # Using pdfplumber for detailed analysis
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📄 Total pages: {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages):
                print(f"\n📄 Page {i+1} analysis:")
                
                # Check for text
                text = page.extract_text()
                if text:
                    lines = text.strip().split('\n')
                    print(f"   📝 Text lines: {len(lines)}")
                    # Show first few lines as sample
                    for j, line in enumerate(lines[:3]):
                        if line.strip():
                            print(f"      {j+1}: {line.strip()[:60]}...")
                
                # Check for form elements
                if hasattr(page, 'within_bbox'):
                    # Look for form-like patterns
                    words = page.extract_words()
                    print(f"   🔤 Words detected: {len(words)}")
                
                # Check for annotations
                if hasattr(page, 'annots'):
                    annots = page.annots
                    if annots:
                        print(f"   📎 Annotations: {len(annots)}")
                
                # Only analyze first 2 pages for brevity
                if i >= 1:
                    break
                    
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")

def clean_pdf_advanced(input_path, output_path):
    """
    Advanced PDF cleaning using multiple methods
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        print(f"📄 Processing {len(reader.pages)} pages...")
        
        for page_num, page in enumerate(reader.pages):
            print(f"🔄 Processing page {page_num + 1}...")
            
            # Method 1: Remove annotations
            if '/Annots' in page:
                print(f"   📎 Removing annotations from page {page_num + 1}")
                # Create a clean copy without annotations
                clean_page = page
                if hasattr(clean_page, 'annotations'):
                    clean_page.annotations = []
                # Remove annotation references
                if '/Annots' in clean_page:
                    del clean_page['/Annots']
            else:
                clean_page = page
            
            # Method 2: Try to remove filled form fields
            if '/AcroForm' in page:
                print(f"   📝 Found form references on page {page_num + 1}")
            
            writer.add_page(clean_page)
        
        # Method 3: Remove document-level form structure
        if reader.trailer.get('/AcroForm'):
            print("🗑️ Removing document-level form structure...")
            # Don't copy the AcroForm to the new document
            pass
        
        # Write the cleaned PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Error in advanced cleaning: {e}")
        return False

def create_truly_blank_template(input_path, output_path):
    """
    Create a blank template by reconstructing the PDF structure
    """
    try:
        print("🏗️ Creating truly blank template...")
        
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Copy page structure but remove content streams that might contain filled text
        for page_num, page in enumerate(reader.pages):
            print(f"   🔄 Reconstructing page {page_num + 1}")
            
            # Create a new page with the same dimensions
            new_page = writer.add_blank_page(
                width=page.mediabox.width,
                height=page.mediabox.height
            )
            
            # Copy essential page attributes but not content
            if '/Resources' in page:
                new_page['/Resources'] = page['/Resources']
            
            # Only copy the basic page structure, not filled content
            # This effectively creates a blank page with the same layout
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
            
        print("✅ Blank template structure created")
        return True
        
    except Exception as e:
        print(f"❌ Error creating blank template: {e}")
        return False

def main():
    """Main function with multiple cleaning strategies"""
    source_file = "/home/ender/.claude/projects/offer-creator/California_Residential_Purchase_Agreement_-_1224_ts77432.pdf"
    
    # Check if source exists
    if not os.path.exists(source_file):
        print(f"❌ Source file not found: {source_file}")
        return False
    
    # Analyze the PDF first
    analyze_pdf_structure(source_file)
    
    # Try multiple output strategies
    outputs = [
        ("California_Residential_Purchase_Agreement_CLEAN_TEMPLATE.pdf", clean_pdf_advanced),
        ("California_Residential_Purchase_Agreement_STRUCTURE_ONLY.pdf", create_truly_blank_template)
    ]
    
    success_count = 0
    
    for output_name, cleaning_func in outputs:
        output_path = f"/home/ender/.claude/projects/offer-creator/{output_name}"
        print(f"\n🎯 Attempting method: {cleaning_func.__name__}")
        print(f"💾 Output: {output_name}")
        
        if cleaning_func(source_file, output_path):
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"✅ Created: {output_name} ({size:,} bytes)")
                success_count += 1
            else:
                print(f"❌ File not created: {output_name}")
        else:
            print(f"❌ Method failed: {cleaning_func.__name__}")
    
    print(f"\n📊 Summary: {success_count}/{len(outputs)} methods successful")
    return success_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)