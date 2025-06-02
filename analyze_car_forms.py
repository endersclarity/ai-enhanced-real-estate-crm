#!/usr/bin/env python3
"""
CAR Forms Analysis Script
Task #2: Analyze CAR Forms and Create Templates

This script analyzes the 13 California Association of Realtors (CAR) forms
to extract field information, coordinates, and create templates for population.
"""

import os
import json
from pathlib import Path
import PyPDF2
import pdfplumber

def analyze_form_with_pypdf2(pdf_path):
    """Analyze PDF form fields using PyPDF2"""
    fields = []
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Get form fields from the PDF
            if reader.is_encrypted:
                print(f"❌ {pdf_path} is encrypted, skipping PyPDF2 analysis")
                return fields
                
            if '/AcroForm' in reader.trailer['/Root']:
                form = reader.trailer['/Root']['/AcroForm']
                if '/Fields' in form:
                    form_fields = form['/Fields']
                    for field_ref in form_fields:
                        field = field_ref.get_object()
                        if '/T' in field:  # Field name
                            field_info = {
                                'name': field['/T'],
                                'type': field.get('/FT', 'Unknown'),
                                'value': field.get('/V', ''),
                                'method': 'PyPDF2'
                            }
                            fields.append(field_info)
    except Exception as e:
        print(f"❌ PyPDF2 error for {pdf_path}: {e}")
    
    return fields

def analyze_form_with_pdfplumber(pdf_path):
    """Analyze PDF form using pdfplumber for text and structure"""
    analysis = {
        'pages': 0,
        'text_blocks': [],
        'fields_detected': [],
        'method': 'pdfplumber'
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            analysis['pages'] = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages):
                # Extract text with positioning
                words = page.extract_words()
                for word in words[:20]:  # First 20 words for analysis
                    analysis['text_blocks'].append({
                        'text': word['text'],
                        'x0': word['x0'],
                        'y0': word['y0'],
                        'x1': word['x1'],
                        'y1': word['y1'],
                        'page': page_num
                    })
                
                # Look for potential form fields (lines, rectangles)
                lines = page.lines
                rects = page.rects
                analysis['fields_detected'].append({
                    'page': page_num,
                    'lines_count': len(lines),
                    'rectangles_count': len(rects)
                })
                
    except Exception as e:
        print(f"❌ pdfplumber error for {pdf_path}: {e}")
    
    return analysis

def analyze_all_forms():
    """Analyze all 13 CAR forms and generate comprehensive report"""
    forms_dir = Path('car_forms')
    results = {}
    
    print("🔍 Analyzing 13 CAR Forms...")
    print("=" * 60)
    
    for pdf_file in forms_dir.glob('*.pdf'):
        form_name = pdf_file.stem
        print(f"\n📄 Analyzing: {form_name}")
        
        # Analyze with both methods
        pypdf2_fields = analyze_form_with_pypdf2(pdf_file)
        pdfplumber_analysis = analyze_form_with_pdfplumber(pdf_file)
        
        results[form_name] = {
            'file_path': str(pdf_file),
            'pypdf2_fields': pypdf2_fields,
            'pdfplumber_analysis': pdfplumber_analysis,
            'field_count_pypdf2': len(pypdf2_fields),
            'pages': pdfplumber_analysis.get('pages', 0),
            'analysis_timestamp': '2025-06-01T06:30:00Z'
        }
        
        print(f"   PyPDF2 fields found: {len(pypdf2_fields)}")
        print(f"   Pages: {pdfplumber_analysis.get('pages', 0)}")
        
        # Show sample fields
        if pypdf2_fields:
            print("   Sample fields:")
            for field in pypdf2_fields[:3]:
                print(f"     - {field['name']} ({field['type']})")
    
    return results

def save_analysis_results(results):
    """Save analysis results to JSON file"""
    output_file = 'car_forms_analysis.json'
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Analysis results saved to: {output_file}")
    return output_file

def generate_summary_report(results):
    """Generate human-readable summary report"""
    print("\n" + "=" * 60)
    print("📊 CAR FORMS ANALYSIS SUMMARY")
    print("=" * 60)
    
    total_forms = len(results)
    total_fields = sum(r['field_count_pypdf2'] for r in results.values())
    total_pages = sum(r['pages'] for r in results.values())
    
    print(f"Total Forms Analyzed: {total_forms}")
    print(f"Total Form Fields Found: {total_fields}")
    print(f"Total Pages: {total_pages}")
    print(f"Average Fields per Form: {total_fields/total_forms:.1f}")
    
    print("\n📋 Forms by Field Count:")
    sorted_forms = sorted(results.items(), key=lambda x: x[1]['field_count_pypdf2'], reverse=True)
    
    for form_name, data in sorted_forms:
        field_count = data['field_count_pypdf2']
        pages = data['pages']
        print(f"   {field_count:3d} fields | {pages:2d} pages | {form_name}")
    
    # Identify key forms for priority analysis
    print("\n🎯 Priority Forms (Most Complex):")
    priority_forms = [form for form, data in sorted_forms[:5]]
    for i, form in enumerate(priority_forms, 1):
        print(f"   {i}. {form}")

if __name__ == "__main__":
    print("🚀 Starting CAR Forms Analysis - Task #2")
    print("Phase A1: PDF Analysis & Template Engine Workstream")
    
    # Ensure forms directory exists
    if not Path('car_forms').exists():
        print("❌ car_forms/ directory not found. Please extract attachments.zip first.")
        exit(1)
    
    # Run comprehensive analysis
    results = analyze_all_forms()
    
    # Save results
    output_file = save_analysis_results(results)
    
    # Generate summary
    generate_summary_report(results)
    
    print("\n✅ Task #2 Analysis Complete!")
    print(f"📊 Results saved to: {output_file}")
    print("🔄 Ready to proceed with Task #3: CRM-to-Form Field Mapping")