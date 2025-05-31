#!/usr/bin/env python3
"""
Comprehensive PDF Security Analysis Report
Analyzes all disclosure forms and provides actionable insights
"""

import PyPDF2
import os
import json
from datetime import datetime

def comprehensive_pdf_analysis():
    """
    Generate comprehensive analysis of all PDF forms
    """
    # Get all PDF files in root directory
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    print("🔍 COMPREHENSIVE PDF SECURITY ANALYSIS")
    print("=" * 70)
    print(f"Found {len(pdf_files)} PDF files to analyze\n")
    
    analysis_results = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_files': 0,
            'encrypted_files': 0,
            'accessible_encrypted': 0,
            'fillable_forms': 0,
            'non_fillable_forms': 0
        },
        'security_patterns': {},
        'software_analysis': {},
        'files': {}
    }
    
    for pdf_file in sorted(pdf_files):
        try:
            with open(pdf_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                file_info = {
                    'file_size': os.path.getsize(pdf_file),
                    'num_pages': len(pdf_reader.pages),
                    'is_encrypted': pdf_reader.is_encrypted,
                    'accessible': False,
                    'has_form_fields': False,
                    'form_field_count': 0,
                    'metadata': {},
                    'security_notes': []
                }
                
                analysis_results['summary']['total_files'] += 1
                
                # Handle encryption
                if pdf_reader.is_encrypted:
                    analysis_results['summary']['encrypted_files'] += 1
                    decrypt_result = pdf_reader.decrypt('')
                    if decrypt_result == 1:
                        file_info['accessible'] = True
                        file_info['security_notes'].append('Encrypted but accessible with empty password')
                        analysis_results['summary']['accessible_encrypted'] += 1
                    else:
                        file_info['security_notes'].append('Encrypted and password-protected')
                else:
                    file_info['accessible'] = True
                    file_info['security_notes'].append('Not encrypted')
                
                # Get metadata if accessible
                if file_info['accessible']:
                    if pdf_reader.metadata:
                        for key, value in pdf_reader.metadata.items():
                            clean_key = key.replace('/', '').replace('\\', '')
                            file_info['metadata'][clean_key] = str(value) if value else None
                    
                    # Check for form fields
                    try:
                        form_fields = pdf_reader.get_form_text_fields()
                        if form_fields:
                            file_info['has_form_fields'] = True
                            file_info['form_field_count'] = len(form_fields)
                            analysis_results['summary']['fillable_forms'] += 1
                        else:
                            analysis_results['summary']['non_fillable_forms'] += 1
                    except:
                        analysis_results['summary']['non_fillable_forms'] += 1
                
                analysis_results['files'][pdf_file] = file_info
                
                # Track software patterns
                producer = file_info['metadata'].get('Producer', '')
                if producer:
                    if producer not in analysis_results['software_analysis']:
                        analysis_results['software_analysis'][producer] = 0
                    analysis_results['software_analysis'][producer] += 1
                
                # Quick status display
                status = "✅" if file_info['accessible'] else "❌"
                form_status = "📝" if file_info['has_form_fields'] else "📄"
                size_mb = file_info['file_size'] / 1024 / 1024
                print(f"{status} {form_status} {pdf_file} ({size_mb:.1f}MB, {file_info['num_pages']} pages)")
                
        except Exception as e:
            print(f"❌ Error analyzing {pdf_file}: {e}")
            analysis_results['files'][pdf_file] = {'error': str(e)}
    
    # Generate insights
    print(f"\n🎯 SECURITY ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"📊 Total Files: {analysis_results['summary']['total_files']}")
    print(f"🔒 Encrypted Files: {analysis_results['summary']['encrypted_files']}")
    print(f"🔓 Accessible Encrypted: {analysis_results['summary']['accessible_encrypted']}")
    print(f"📝 Fillable Forms: {analysis_results['summary']['fillable_forms']}")
    print(f"📄 Non-Fillable: {analysis_results['summary']['non_fillable_forms']}")
    
    print(f"\n🔧 SOFTWARE ANALYSIS")
    print("-" * 30)
    for software, count in analysis_results['software_analysis'].items():
        print(f"• {software}: {count} files")
    
    # Identify key findings
    print(f"\n🔍 KEY FINDINGS")
    print("-" * 30)
    
    if analysis_results['summary']['encrypted_files'] == analysis_results['summary']['accessible_encrypted']:
        print("✅ ALL encrypted files use empty password protection")
        print("✅ Workaround: Use pdf_reader.decrypt('') for all forms")
    
    if 'Fonet' in str(analysis_results['software_analysis']):
        print("🏢 Forms generated by Fonet (likely ZipForm system)")
        print("📅 All forms appear to be recent (2024-2025)")
    
    if analysis_results['summary']['fillable_forms'] == 0:
        print("⚠️  NO fillable form fields detected in any PDF")
        print("💡 May need text overlay or coordinate-based filling")
    
    # Save detailed report
    with open('comprehensive_security_analysis.json', 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed analysis saved to: comprehensive_security_analysis.json")
    
    return analysis_results

if __name__ == "__main__":
    comprehensive_pdf_analysis()