#!/usr/bin/env python3
"""
Create a test California Purchase Agreement with sample client data
"""

from pdf_form_creator import PDFFormCreator
import os

def create_test_form():
    """Create a test form with sample client data"""
    creator = PDFFormCreator()
    
    # Create the base form
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "test_CPA.pdf")
    
    # Create the form
    result = creator.create_california_purchase_agreement(output_path)
    
    if result:
        file_size = os.path.getsize(output_path)
        print(f"✅ Test California Purchase Agreement created successfully!")
        print(f"📁 File: {output_path}")
        print(f"📊 Size: {file_size:,} bytes")
        print(f"🌐 Windows path: \\\\wsl.localhost\\Ubuntu\\home\\ender\\.claude\\projects\\offer-creator\\{output_path}")
        
        return output_path
    else:
        print("❌ Failed to create test form")
        return None

if __name__ == "__main__":
    create_test_form()