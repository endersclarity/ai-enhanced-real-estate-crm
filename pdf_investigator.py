#!/usr/bin/env python3
"""
PDF Investigator - Analyze the CLEAN_TEMPLATE.pdf to understand its structure
Find out what the "blue text" is and how to remove it while preserving form fields
"""

import fitz  # pymupdf
import pdfplumber
from PyPDF2 import PdfReader
import fillpdf
import os

class PDFInvestigator:
    def __init__(self, pdf_path="documents/California_Residential_Purchase_Agreement_CLEAN_TEMPLATE.pdf"):
        self.pdf_path = pdf_path
        
    def analyze_with_pymupdf(self):
        """Analyze PDF using PyMuPDF (fitz)"""
        print("🔍 ANALYZING WITH PYMUPDF (FITZ)")
        print("=" * 50)
        
        doc = fitz.open(self.pdf_path)
        print(f"📄 Pages: {len(doc)}")
        print(f"🔒 Encrypted: {doc.is_encrypted}")
        
        # Get form fields
        total_fields = 0
        for page_num in range(len(doc)):
            page = doc[page_num]
            fields = list(page.widgets())
            total_fields += len(fields)
        
        print(f"📝 Total Form Fields: {total_fields}")
        
        if total_fields > 0:
            print(f"\n📋 FORM FIELDS FOUND:")
            for page_num in range(len(doc)):
                page = doc[page_num]
                fields = list(page.widgets())
                print(f"  Page {page_num + 1}: {len(fields)} fields")
                
                for i, field in enumerate(fields):
                    print(f"    Field {i+1}:")
                    print(f"      Name: {field.field_name}")
                    print(f"      Type: {field.field_type}")
                    print(f"      Value: {field.field_value}")
                    print(f"      Rect: {field.rect}")
                    if field.field_value:
                        print(f"      ⚠️  HAS VALUE (possible blue text): '{field.field_value}'")
                    print()
        
        # Check for text and colors
        print(f"\n🎨 TEXT AND COLORS:")
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_dict = page.get_text("dict")
            
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            color = span.get("color", 0)
                            text = span.get("text", "").strip()
                            if text and color != 0:  # Non-black text
                                print(f"      Colored text (color={color}): '{text}'")
        
        doc.close()
        return True
    
    def analyze_with_pdfplumber(self):
        """Analyze PDF using pdfplumber"""
        print("\n🔍 ANALYZING WITH PDFPLUMBER")
        print("=" * 50)
        
        with pdfplumber.open(self.pdf_path) as pdf:
            print(f"📄 Pages: {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages):
                print(f"\nPage {i+1}:")
                
                # Check for form fields
                if hasattr(page, 'annots') and page.annots:
                    print(f"  📋 Annotations: {len(page.annots)}")
                    for annot in page.annots:
                        print(f"    {annot}")
                
                # Extract text
                text = page.extract_text()
                if text:
                    lines = text.split('\n')
                    filled_lines = [line.strip() for line in lines if line.strip()]
                    print(f"  📝 Text lines: {len(filled_lines)}")
                    
                    # Look for potential form data (lines that look like filled fields)
                    for line in filled_lines[:10]:  # First 10 lines
                        if any(char.isdigit() for char in line) or '@' in line or '(' in line:
                            print(f"    Potential data: '{line}'")
    
    def analyze_with_fillpdf(self):
        """Analyze PDF using fillpdf"""
        print("\n🔍 ANALYZING WITH FILLPDF")
        print("=" * 50)
        
        try:
            # Get form fields
            fields = fillpdf.get_form_fields(self.pdf_path)
            if fields:
                print(f"📋 Form fields found: {len(fields)}")
                for field_name, field_info in fields.items():
                    print(f"  {field_name}: {field_info}")
            else:
                print("❌ No form fields detected")
                
        except Exception as e:
            print(f"❌ Error with fillpdf: {e}")
    
    def analyze_with_pypdf2(self):
        """Analyze PDF using PyPDF2"""
        print("\n🔍 ANALYZING WITH PYPDF2")
        print("=" * 50)
        
        try:
            reader = PdfReader(self.pdf_path)
            print(f"📄 Pages: {len(reader.pages)}")
            print(f"🔒 Encrypted: {reader.is_encrypted}")
            
            # Check for form fields
            if "/AcroForm" in reader.trailer["/Root"]:
                print("📋 AcroForm detected")
                form = reader.trailer["/Root"]["/AcroForm"]
                if "/Fields" in form:
                    fields = form["/Fields"]
                    print(f"   Fields array length: {len(fields)}")
            else:
                print("❌ No AcroForm found")
                
        except Exception as e:
            print(f"❌ Error with PyPDF2: {e}")
    
    def extract_sample_content(self):
        """Extract first page content to understand what we're dealing with"""
        print("\n📄 SAMPLE CONTENT EXTRACTION")
        print("=" * 50)
        
        doc = fitz.open(self.pdf_path)
        page = doc[0]
        
        # Extract all text
        text = page.get_text()
        lines = text.split('\n')[:20]  # First 20 lines
        
        print("First 20 lines of text:")
        for i, line in enumerate(lines, 1):
            if line.strip():
                print(f"{i:2d}: {line}")
        
        doc.close()
    
    def create_field_clearing_test(self):
        """Test different methods to clear form fields"""
        print("\n🧪 TESTING FIELD CLEARING METHODS")
        print("=" * 50)
        
        # Test 1: PyMuPDF field clearing
        try:
            doc = fitz.open(self.pdf_path)
            
            # Count total fields first
            total_fields = 0
            for page_num in range(len(doc)):
                page = doc[page_num]
                fields = list(page.widgets())
                total_fields += len(fields)
            
            if total_fields > 0:
                print("✅ PyMuPDF can read form fields - attempting to clear...")
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    fields = list(page.widgets())
                    
                    for field in fields:
                        if field.field_value:
                            print(f"  Clearing field '{field.field_name}': '{field.field_value}'")
                            field.field_value = ""
                            field.update()
                
                # Save test version
                test_output = "output/test_cleared_pymupdf.pdf"
                os.makedirs("output", exist_ok=True)
                doc.save(test_output)
                print(f"💾 Saved cleared version: {test_output}")
                
            doc.close()
            
        except Exception as e:
            print(f"❌ PyMuPDF clearing failed: {e}")

def main():
    """Run comprehensive PDF investigation"""
    investigator = PDFInvestigator()
    
    print("🕵️ PDF INVESTIGATION REPORT")
    print("Analyzing: California_Residential_Purchase_Agreement_CLEAN_TEMPLATE.pdf")
    print("=" * 80)
    
    # Run all analysis methods
    investigator.analyze_with_pymupdf()
    investigator.analyze_with_pdfplumber() 
    investigator.analyze_with_fillpdf()
    investigator.analyze_with_pypdf2()
    investigator.extract_sample_content()
    investigator.create_field_clearing_test()
    
    print("\n🎯 INVESTIGATION COMPLETE")
    print("Check the output above to understand the PDF structure and plan next steps.")

if __name__ == "__main__":
    main()