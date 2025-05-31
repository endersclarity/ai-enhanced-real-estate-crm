#!/usr/bin/env python3
"""
PDF Metadata and Security Analysis Tool
Analyzes password protection and metadata of California disclosure forms
"""

import PyPDF2
import os
import json
from datetime import datetime

def analyze_pdf_metadata(file_path):
    """
    Analyze PDF metadata and security properties
    """
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Basic info
            info = {
                'file_name': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'num_pages': len(pdf_reader.pages),
                'is_encrypted': pdf_reader.is_encrypted,
                'metadata': {},
                'security_info': {},
                'error': None
            }
            
            # Get metadata
            if pdf_reader.metadata:
                for key, value in pdf_reader.metadata.items():
                    # Clean up the key name
                    clean_key = key.replace('/', '').replace('\\', '')
                    info['metadata'][clean_key] = str(value) if value else None
            
            # Security analysis
            if pdf_reader.is_encrypted:
                info['security_info']['encrypted'] = True
                
                # Try to decrypt with empty password (common for "secure" but not password-protected PDFs)
                try:
                    decrypt_result = pdf_reader.decrypt('')
                    info['security_info']['empty_password_works'] = decrypt_result == 1
                    if decrypt_result == 1:
                        info['security_info']['status'] = 'Encrypted but accessible with empty password'
                    else:
                        info['security_info']['status'] = 'Encrypted and password-protected'
                except Exception as e:
                    info['security_info']['decrypt_error'] = str(e)
                
                # Try common passwords
                common_passwords = ['', 'password', '123456', 'admin', 'user']
                for pwd in common_passwords:
                    try:
                        result = pdf_reader.decrypt(pwd)
                        if result == 1:
                            info['security_info'][f'password_found'] = pwd if pwd else 'empty'
                            break
                    except:
                        continue
                        
            else:
                info['security_info']['encrypted'] = False
                info['security_info']['status'] = 'Not encrypted'
            
            # Try to get document info even if encrypted
            try:
                if hasattr(pdf_reader, 'documentInfo') and pdf_reader.documentInfo:
                    for key, value in pdf_reader.documentInfo.items():
                        clean_key = key.replace('/', '').replace('\\', '')
                        info['metadata'][clean_key] = str(value) if value else None
            except Exception as e:
                info['security_info']['metadata_access_error'] = str(e)
                
            return info
            
    except Exception as e:
        return {
            'file_name': os.path.basename(file_path),
            'error': str(e),
            'accessible': False
        }

def main():
    """
    Analyze all main PDF forms in the project root
    """
    # Target PDF files in root directory
    target_files = [
        'California_Residential_Purchase_Agreement_-_1224_ts77432.pdf',
        'Buyer_Representation_and_Broker_Compensation_Agreement_-_1224_ts74307.pdf',
        'Statewide_Buyer_and_Seller_Advisory_-_624_ts89932.pdf',
        'Confidentiality_and_Non-Disclosure_Agreement_-_1221_ts85245.pdf',
        'Market_Conditions_Advisory_-_624_ts88371.pdf',
        'Transaction_Record_-_724_ts71184.pdf',
        'Agent_Visual_Inspection_Disclosure_1_-_624_ts99307.pdf'
    ]
    
    print("🔍 PDF METADATA AND SECURITY ANALYSIS")
    print("=" * 60)
    
    results = {}
    
    for filename in target_files:
        file_path = f'/home/ender/.claude/projects/offer-creator/{filename}'
        if os.path.exists(file_path):
            print(f"\n📄 Analyzing: {filename}")
            print("-" * 40)
            
            result = analyze_pdf_metadata(file_path)
            results[filename] = result
            
            if result.get('error'):
                print(f"❌ ERROR: {result['error']}")
                continue
                
            # Display key information
            print(f"📊 File Size: {result['file_size']:,} bytes")
            print(f"📑 Pages: {result['num_pages']}")
            print(f"🔒 Encrypted: {result['is_encrypted']}")
            
            if result['is_encrypted']:
                print(f"🛡️  Security Status: {result['security_info'].get('status', 'Unknown')}")
                if 'password_found' in result['security_info']:
                    pwd = result['security_info']['password_found']
                    print(f"🔑 Password Found: {'(empty)' if pwd == 'empty' else pwd}")
            
            # Show metadata
            if result['metadata']:
                print("\n📋 METADATA:")
                for key, value in result['metadata'].items():
                    if value and key in ['Creator', 'Producer', 'Author', 'Title', 'Subject', 'CreationDate', 'ModDate']:
                        print(f"  {key}: {value}")
            
        else:
            print(f"❌ File not found: {filename}")
            results[filename] = {'error': 'File not found', 'accessible': False}
    
    # Save detailed results to JSON
    output_file = 'pdf_metadata_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    # Summary analysis
    print(f"\n🎯 SECURITY SUMMARY")
    print("=" * 40)
    
    encrypted_count = 0
    accessible_count = 0
    total_analyzed = 0
    
    for filename, result in results.items():
        if not result.get('error'):
            total_analyzed += 1
            if result['is_encrypted']:
                encrypted_count += 1
                if result['security_info'].get('empty_password_works') or 'password_found' in result['security_info']:
                    accessible_count += 1
    
    print(f"📊 Total Forms Analyzed: {total_analyzed}")
    print(f"🔒 Encrypted Forms: {encrypted_count}")
    print(f"🔓 Accessible Encrypted Forms: {accessible_count}")
    
    if encrypted_count > 0:
        print(f"\n🔧 POTENTIAL WORKAROUNDS:")
        print("- Use PyPDF2.decrypt('') for forms with empty password protection")
        print("- Consider PDF reconstruction/text extraction for inaccessible forms")
        print("- Check if forms can be opened in Adobe Reader and re-saved")

if __name__ == "__main__":
    main()