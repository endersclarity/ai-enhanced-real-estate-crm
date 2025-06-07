#!/usr/bin/env python3
"""
PDF Output Validation Script
Generates and validates PDF output for all 5 CAR forms with comprehensive content analysis
"""

import requests
import json
import os
import time
from datetime import datetime
import PyPDF2

# Configuration
BASE_URL = "http://172.22.206.209:5000"
API_URL = f"{BASE_URL}/api/forms/quick-generate"
OUTPUT_DIR = "test_output"

def ensure_output_dir():
    """Ensure output directory exists"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def generate_test_pdfs():
    """Generate PDF for each form type with comprehensive test data"""
    
    test_forms = {
        "statewide_buyer_seller_advisory": {
            "client_name": "Sarah Johnson",
            "client_phone": "916-555-1234",
            "client_email": "sarah.johnson@email.com",
            "property_address": "1234 Oak Street",
            "property_city": "Sacramento",
            "property_type": "Single Family Home",
            "transaction_type": "Purchase"
        },
        "buyer_representation_agreement": {
            "client_name": "Michael Chen",
            "client_phone": "916-555-2345",
            "client_email": "michael.chen@email.com",
            "client_address": "5678 Pine Avenue\nSacramento, CA 95814",
            "agent_name": "Narissa Henderson",
            "agent_license": "DRE12345678",
            "brokerage_name": "Narissa Realty Group",
            "commission_rate": "3.0"
        },
        "agent_visual_inspection_disclosure": {
            "client_name": "Jennifer Martinez",
            "property_address": "9876 Elm Drive",
            "property_city": "Davis",
            "property_type": "Condominium",
            "inspection_date": "2025-06-15",
            "agent_name": "Narissa Henderson",
            "agent_license": "DRE12345678",
            "brokerage_name": "Narissa Realty Group"
        },
        "market_conditions_advisory": {
            "client_name": "Robert Williams",
            "client_phone": "916-555-3456",
            "client_email": "robert.williams@email.com",
            "target_city": "Roseville",
            "property_type": "Townhouse",
            "transaction_type": "Purchase",
            "agent_name": "Narissa Henderson",
            "agent_license": "DRE12345678",
            "brokerage_name": "Narissa Realty Group"
        },
        "transaction_record": {
            "buyer_name": "Lisa Thompson",
            "buyer_phone": "916-555-4567",
            "buyer_email": "lisa.thompson@email.com",
            "property_address": "2468 Maple Lane",
            "purchase_price": "875000",
            "earnest_money": "25000",
            "contract_date": "2025-06-10",
            "closing_date": "2025-07-15",
            "listing_agent": "Jane Smith",
            "buyer_agent": "Narissa Henderson"
        }
    }
    
    generated_files = {}
    
    print("🚀 Generating PDFs for all 5 CAR forms...")
    print("=" * 60)
    
    for form_type, test_data in test_forms.items():
        print(f"\n📄 Generating {form_type}...")
        
        try:
            payload = {
                "form_type": form_type,
                "quick_data": test_data,
                "generation_method": "quick_form"
            }
            
            start_time = time.time()
            response = requests.post(API_URL, json=payload, timeout=30)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    output_file = result.get('output_file')
                    populated_fields = result.get('populated_fields', 'Unknown')
                    
                    print(f"  ✅ Generated successfully")
                    print(f"  📁 File: {output_file}")
                    print(f"  📊 Fields populated: {populated_fields}")
                    print(f"  ⏱️ Generation time: {generation_time:.2f}s")
                    
                    generated_files[form_type] = {
                        'filename': output_file,
                        'populated_fields': populated_fields,
                        'generation_time': generation_time,
                        'test_data': test_data
                    }
                else:
                    print(f"  ❌ Generation failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"  ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")
    
    return generated_files

def analyze_pdf_content(pdf_path):
    """Analyze PDF content for validation"""
    try:
        # Check if file exists in current directory or output directory
        if not os.path.exists(pdf_path):
            output_path = os.path.join('output', pdf_path)
            if os.path.exists(output_path):
                pdf_path = output_path
            else:
                return {"error": f"PDF file not found: {pdf_path} or {output_path}"}
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            analysis = {
                "pages": len(pdf_reader.pages),
                "text_content": "",
                "file_size": os.path.getsize(pdf_path),
                "valid_pdf": True
            }
            
            # Extract text from all pages
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    analysis["text_content"] += page_text
                except Exception as e:
                    analysis[f"page_{page_num}_error"] = str(e)
            
            return analysis
            
    except Exception as e:
        return {"error": f"PDF analysis failed: {e}", "valid_pdf": False}

def validate_field_population(generated_files):
    """Validate that test data appears in generated PDFs"""
    
    print("\n🔍 Validating Field Population in Generated PDFs")
    print("=" * 60)
    
    validation_results = {}
    
    for form_type, file_info in generated_files.items():
        print(f"\n📋 Validating {form_type}...")
        
        pdf_path = file_info['filename']
        test_data = file_info['test_data']
        
        # Analyze PDF content
        analysis = analyze_pdf_content(pdf_path)
        
        if analysis.get('error'):
            print(f"  ❌ PDF Analysis Error: {analysis['error']}")
            validation_results[form_type] = {"valid": False, "error": analysis['error']}
            continue
        
        print(f"  📄 Pages: {analysis['pages']}")
        print(f"  💾 Size: {analysis['file_size']} bytes")
        
        # Check for field population
        pdf_text = analysis['text_content'].lower()
        populated_fields = []
        missing_fields = []
        
        for field_name, field_value in test_data.items():
            # Convert field value to string and check if it appears in PDF
            value_str = str(field_value).lower()
            
            # Skip very short values that might cause false positives
            if len(value_str) > 2 and value_str in pdf_text:
                populated_fields.append(f"{field_name}: {field_value}")
            else:
                missing_fields.append(f"{field_name}: {field_value}")
        
        population_rate = len(populated_fields) / len(test_data) * 100
        
        print(f"  ✅ Populated fields ({len(populated_fields)}):")
        for field in populated_fields[:3]:  # Show first 3
            print(f"    - {field}")
        if len(populated_fields) > 3:
            print(f"    ... and {len(populated_fields) - 3} more")
        
        if missing_fields:
            print(f"  ⚠️ Missing/undetected fields ({len(missing_fields)}):")
            for field in missing_fields[:3]:  # Show first 3
                print(f"    - {field}")
            if len(missing_fields) > 3:
                print(f"    ... and {len(missing_fields) - 3} more")
        
        print(f"  📊 Population rate: {population_rate:.1f}%")
        
        validation_results[form_type] = {
            "valid": analysis['valid_pdf'],
            "population_rate": population_rate,
            "populated_fields": len(populated_fields),
            "total_fields": len(test_data),
            "pdf_pages": analysis['pages'],
            "pdf_size": analysis['file_size']
        }
    
    return validation_results

def generate_validation_report(generated_files, validation_results):
    """Generate comprehensive validation report"""
    
    print("\n📊 COMPREHENSIVE VALIDATION REPORT")
    print("=" * 60)
    
    total_forms = len(generated_files)
    successful_generations = len([f for f in generated_files.values() if f])
    valid_pdfs = len([r for r in validation_results.values() if r.get('valid', False)])
    
    print(f"📋 Form Generation Summary:")
    print(f"  Total forms tested: {total_forms}")
    print(f"  Successful generations: {successful_generations}")
    print(f"  Valid PDFs created: {valid_pdfs}")
    print(f"  Success rate: {successful_generations/total_forms*100:.1f}%")
    
    print(f"\n⚡ Performance Summary:")
    avg_generation_time = sum(f.get('generation_time', 0) for f in generated_files.values()) / len(generated_files)
    print(f"  Average generation time: {avg_generation_time:.2f}s")
    print(f"  Target met (<5s): {'✅ Yes' if avg_generation_time < 5.0 else '❌ No'}")
    
    print(f"\n📄 PDF Quality Summary:")
    avg_population_rate = sum(r.get('population_rate', 0) for r in validation_results.values()) / len(validation_results)
    print(f"  Average field population: {avg_population_rate:.1f}%")
    
    total_pdf_size = sum(r.get('pdf_size', 0) for r in validation_results.values())
    print(f"  Total PDF size: {total_pdf_size:,} bytes")
    
    print(f"\n🎯 Quality Metrics:")
    quality_score = (successful_generations + valid_pdfs + (1 if avg_generation_time < 5.0 else 0)) / 3
    print(f"  Overall quality score: {quality_score:.1f}/3.0")
    
    if quality_score >= 2.5:
        print(f"  📈 Status: ✅ PRODUCTION READY")
    elif quality_score >= 2.0:
        print(f"  📈 Status: ⚠️ NEEDS MINOR IMPROVEMENTS")
    else:
        print(f"  📈 Status: ❌ NEEDS MAJOR IMPROVEMENTS")
    
    # Detailed form breakdown
    print(f"\n📋 Detailed Form Analysis:")
    for form_type in generated_files.keys():
        file_info = generated_files.get(form_type, {})
        validation_info = validation_results.get(form_type, {})
        
        status = "✅" if validation_info.get('valid', False) else "❌"
        population = validation_info.get('population_rate', 0)
        gen_time = file_info.get('generation_time', 0)
        
        print(f"  {status} {form_type}:")
        print(f"    Population: {population:.1f}% | Time: {gen_time:.2f}s | Pages: {validation_info.get('pdf_pages', 'N/A')}")

def main():
    """Run comprehensive PDF validation"""
    print("🧪 PDF Output Validation Suite")
    print("=" * 60)
    print(f"Target URL: {API_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    ensure_output_dir()
    
    # Generate test PDFs
    generated_files = generate_test_pdfs()
    
    if not generated_files:
        print("❌ No PDFs were generated successfully. Aborting validation.")
        return False
    
    # Validate PDF content
    validation_results = validate_field_population(generated_files)
    
    # Generate report
    generate_validation_report(generated_files, validation_results)
    
    # Overall success check
    all_valid = all(r.get('valid', False) for r in validation_results.values())
    good_population = all(r.get('population_rate', 0) > 50 for r in validation_results.values())
    
    if all_valid and good_population:
        print("\n🎉 PDF VALIDATION PASSED: All forms generate valid PDFs with good field population!")
        return True
    else:
        print("\n⚠️ PDF VALIDATION ISSUES: Some forms need improvement.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)