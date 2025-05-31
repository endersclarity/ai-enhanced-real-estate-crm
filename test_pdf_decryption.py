#!/usr/bin/env python3
"""
Test PDF Decryption and Field Access
Tests the practical workaround for password-protected PDFs
"""

import PyPDF2
import os

def test_pdf_access(file_path):
    """
    Test if we can decrypt and access form fields in a PDF
    """
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"\n📄 Testing: {os.path.basename(file_path)}")
            print("-" * 50)
            
            # Check encryption status
            if pdf_reader.is_encrypted:
                print("🔒 PDF is encrypted")
                
                # Try to decrypt with empty password
                decrypt_result = pdf_reader.decrypt('')
                if decrypt_result == 1:
                    print("✅ Successfully decrypted with empty password")
                else:
                    print("❌ Failed to decrypt with empty password")
                    return False
            else:
                print("🔓 PDF is not encrypted")
            
            # Test field access
            try:
                form_fields = pdf_reader.get_form_text_fields()
                if form_fields:
                    print(f"📝 Found {len(form_fields)} form fields:")
                    # Show first 5 fields as examples
                    for i, (field_name, field_value) in enumerate(list(form_fields.items())[:5]):
                        print(f"  {i+1}. {field_name}: {field_value or '(empty)'}")
                    if len(form_fields) > 5:
                        print(f"  ... and {len(form_fields) - 5} more fields")
                else:
                    print("📝 No fillable form fields detected")
                    
                # Test page access
                first_page = pdf_reader.pages[0]
                page_text = first_page.extract_text()[:200]
                print(f"📖 Page text sample: {page_text}...")
                
                return True
                
            except Exception as e:
                print(f"❌ Error accessing form fields: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error opening PDF: {e}")
        return False

def main():
    """
    Test decryption and field access on key PDF forms
    """
    test_files = [
        'California_Residential_Purchase_Agreement_-_1224_ts77432.pdf',
        'Buyer_Representation_and_Broker_Compensation_Agreement_-_1224_ts74307.pdf',
        'Statewide_Buyer_and_Seller_Advisory_-_624_ts89932.pdf'
    ]
    
    print("🔓 PDF DECRYPTION AND FIELD ACCESS TEST")
    print("=" * 60)
    
    success_count = 0
    total_count = 0
    
    for filename in test_files:
        file_path = f'/home/ender/.claude/projects/offer-creator/{filename}'
        if os.path.exists(file_path):
            total_count += 1
            if test_pdf_access(file_path):
                success_count += 1
        else:
            print(f"❌ File not found: {filename}")
    
    print(f"\n🎯 SUMMARY")
    print("=" * 30)
    print(f"✅ Successfully accessed: {success_count}/{total_count} files")
    print(f"🔧 Workaround status: {'WORKING' if success_count == total_count else 'PARTIAL'}")
    
    if success_count == total_count:
        print("\n💡 RECOMMENDED APPROACH:")
        print("Use pdf_reader.decrypt('') before accessing form fields")
        print("This bypasses the password protection on these forms")

if __name__ == "__main__":
    main()