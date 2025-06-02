#!/usr/bin/env python3
"""
CAR Forms Field Analysis Script
Analyzes all 13 CAR forms to extract field information and create templates
Part of Task #2: Analyze CAR Forms and Create Templates
"""

import os
import json
import pdfplumber
from pathlib import Path
from datetime import datetime

def analyze_form_fields(pdf_path):
    """Analyze a single PDF form to extract field information"""
    form_data = {
        "filename": os.path.basename(pdf_path),
        "path": str(pdf_path),
        "fields": [],
        "pages": 0,
        "analysis_date": datetime.now().isoformat()
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            form_data["pages"] = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract text elements that might be form fields
                chars = page.chars
                
                # Look for text patterns that suggest form fields
                page_fields = []
                
                # Extract all text with coordinates
                for char in chars:
                    if char.get('text', '').strip():
                        field_info = {
                            "page": page_num,
                            "text": char['text'],
                            "x": char['x0'],
                            "y": char['y0'],
                            "width": char['x1'] - char['x0'],
                            "height": char['y1'] - char['y0'],
                            "font": char.get('fontname', 'unknown'),
                            "size": char.get('size', 0)
                        }
                        page_fields.append(field_info)
                
                # Try to detect form fields from PDF structure
                if hasattr(page, 'annots'):
                    for annot in page.annots or []:
                        if annot.get('subtype') == 'Widget':  # Form field
                            field_info = {
                                "page": page_num,
                                "type": "form_field",
                                "name": annot.get('T', 'unnamed_field'),
                                "value": annot.get('V', ''),
                                "rect": annot.get('Rect', []),
                                "field_type": annot.get('FT', 'unknown')
                            }
                            page_fields.append(field_info)
                
                form_data["fields"].extend(page_fields)
                
    except Exception as e:
        form_data["error"] = str(e)
        print(f"Error analyzing {pdf_path}: {e}")
    
    return form_data

def analyze_all_forms():
    """Analyze all CAR forms and generate comprehensive report"""
    car_forms_dir = Path("car_forms")
    output_file = "car_forms_analysis.json"
    
    if not car_forms_dir.exists():
        print(f"Error: {car_forms_dir} directory not found")
        return
    
    analysis_results = {
        "analysis_metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_forms": 0,
            "script_version": "1.0",
            "purpose": "Extract field information from 13 CAR forms for automated population"
        },
        "forms": []
    }
    
    # Get all PDF files
    pdf_files = list(car_forms_dir.glob("*.pdf"))
    analysis_results["analysis_metadata"]["total_forms"] = len(pdf_files)
    
    print(f"Found {len(pdf_files)} CAR forms to analyze...")
    
    for pdf_file in sorted(pdf_files):
        print(f"Analyzing: {pdf_file.name}")
        form_analysis = analyze_form_fields(pdf_file)
        analysis_results["forms"].append(form_analysis)
    
    # Save analysis results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Analysis complete! Results saved to {output_file}")
    
    # Generate summary report
    print("\n📊 ANALYSIS SUMMARY:")
    print(f"Total forms analyzed: {len(analysis_results['forms'])}")
    
    for form in analysis_results["forms"]:
        field_count = len(form.get("fields", []))
        pages = form.get("pages", 0)
        error = form.get("error")
        status = "❌ ERROR" if error else "✅ SUCCESS"
        
        print(f"  {form['filename']}: {field_count} elements, {pages} pages {status}")
        if error:
            print(f"    Error: {error}")
    
    return analysis_results

def create_form_templates():
    """Create blank template structure for form population"""
    templates_dir = Path("form_templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Load analysis results
    if not Path("car_forms_analysis.json").exists():
        print("❌ No analysis file found. Run analysis first.")
        return
    
    with open("car_forms_analysis.json", 'r') as f:
        analysis = json.load(f)
    
    templates = {}
    
    for form in analysis["forms"]:
        form_name = form["filename"].replace(".pdf", "")
        template = {
            "form_name": form_name,
            "source_file": form["filename"],
            "pages": form.get("pages", 0),
            "field_mappings": {},
            "template_created": datetime.now().isoformat()
        }
        
        # Create field mapping structure
        fields = form.get("fields", [])
        for i, field in enumerate(fields):
            field_id = f"field_{i:03d}"
            template["field_mappings"][field_id] = {
                "page": field.get("page", 1),
                "coordinates": {
                    "x": field.get("x", 0),
                    "y": field.get("y", 0),
                    "width": field.get("width", 0),
                    "height": field.get("height", 0)
                },
                "text_content": field.get("text", ""),
                "field_type": field.get("type", "text"),
                "crm_mapping": None  # To be filled in Task #3
            }
        
        templates[form_name] = template
        
        # Save individual template file
        template_file = templates_dir / f"{form_name}_template.json"
        with open(template_file, 'w') as f:
            json.dump(template, f, indent=2)
    
    # Save consolidated templates file
    with open("car_form_templates.json", 'w') as f:
        json.dump(templates, f, indent=2)
    
    print(f"\n✅ Templates created!")
    print(f"Individual templates: {templates_dir}/")
    print(f"Consolidated file: car_form_templates.json")
    
    return templates

if __name__ == "__main__":
    print("🔍 CAR Forms Analysis Script")
    print("=" * 50)
    
    # Step 1: Analyze all forms
    print("\n📋 Step 1: Analyzing all CAR forms...")
    analysis_results = analyze_all_forms()
    
    if analysis_results:
        # Step 2: Create templates
        print("\n📋 Step 2: Creating form templates...")
        templates = create_form_templates()
        
        print(f"\n🎉 Task #2 Progress:")
        print(f"✅ Analyzed {len(analysis_results['forms'])} CAR forms")
        print(f"✅ Created templates for form population")
        print(f"✅ Ready for Task #3: CRM field mapping")