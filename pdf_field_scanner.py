#!/usr/bin/env python3
"""
PDF Field Scanner - Extract all form field names for CSV mapping
Handles field names with spaces and creates intelligent mapping
"""

import pypdfium2 as pdfium
import PyPDF2
import json
import re
from pathlib import Path

class PDFFieldScanner:
    def __init__(self):
        self.field_mappings = {}
        
    def scan_with_pypdfium2(self, pdf_path):
        """Extract form fields using pypdfium2 (Google's library)"""
        try:
            doc = pdfium.PdfDocument(pdf_path)
            fields = {}
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get form fields on this page
                for field in page.get_form_fields():
                    field_name = field.get_name()
                    field_type = field.get_type()
                    field_value = field.get_value()
                    
                    fields[field_name] = {
                        'type': field_type,
                        'value': field_value,
                        'page': page_num
                    }
            
            doc.close()
            return fields
            
        except Exception as e:
            print(f"pypdfium2 error: {e}")
            return {}
    
    def scan_with_pypdf2(self, pdf_path):
        """Fallback: Extract form fields using PyPDF2"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                fields = {}
                
                if reader.form_fields:
                    for field_name, field_info in reader.form_fields.items():
                        fields[field_name] = {
                            'type': field_info.get('/FT', 'unknown'),
                            'value': field_info.get('/V', ''),
                            'page': 'unknown'
                        }
                
                return fields
                
        except Exception as e:
            print(f"PyPDF2 error: {e}")
            return {}
    
    def create_csv_mapping(self, fields):
        """Create intelligent CSV column mapping from field names"""
        mapping = {}
        
        for field_name in fields.keys():
            # Convert field name to CSV-friendly column
            csv_column = self.normalize_field_name(field_name)
            mapping[csv_column] = field_name
            
        return mapping
    
    def normalize_field_name(self, field_name):
        """Convert PDF field name to CSV column name"""
        # Handle common patterns
        normalized = field_name.lower()
        
        # Replace spaces with underscores
        normalized = re.sub(r'\s+', '_', normalized)
        
        # Remove special characters
        normalized = re.sub(r'[^\w_]', '', normalized)
        
        # Handle common field mappings
        mappings = {
            'buyer_first_name': 'buyer_first_name',
            'buyer_last_name': 'buyer_last_name', 
            'buyer_name': 'buyer_name',
            'purchase_price': 'purchase_price',
            'property_address': 'property_address',
            'earnest_money': 'earnest_money',
            'agent_name': 'agent_name',
            'agent_phone': 'agent_phone',
            'closing_date': 'closing_date'
        }
        
        return mappings.get(normalized, normalized)
    
    def scan_pdf(self, pdf_path):
        """Main scanning function - tries both libraries"""
        print(f"\n🔍 Scanning PDF: {pdf_path}")
        
        # Try pypdfium2 first (more reliable)
        fields = self.scan_with_pypdfium2(pdf_path)
        
        if not fields:
            print("   Trying PyPDF2 fallback...")
            fields = self.scan_with_pypdf2(pdf_path)
        
        if fields:
            print(f"   ✅ Found {len(fields)} form fields")
            
            # Create CSV mapping
            csv_mapping = self.create_csv_mapping(fields)
            
            return {
                'fields': fields,
                'csv_mapping': csv_mapping,
                'field_count': len(fields)
            }
        else:
            print("   ❌ No form fields found")
            return None
    
    def save_mapping(self, scan_result, output_file):
        """Save field mapping to JSON file"""
        if scan_result:
            with open(output_file, 'w') as f:
                json.dump(scan_result, f, indent=2)
            print(f"   💾 Mapping saved to {output_file}")

def main():
    """Test the scanner with available PDFs"""
    scanner = PDFFieldScanner()
    
    # Find PDF files in current directory
    pdf_files = list(Path('.').glob('*.pdf'))
    
    if not pdf_files:
        print("No PDF files found in current directory")
        return
    
    print(f"Found {len(pdf_files)} PDF files to scan:")
    
    all_results = {}
    
    for pdf_file in pdf_files[:5]:  # Limit to first 5 files
        result = scanner.scan_pdf(str(pdf_file))
        
        if result:
            all_results[str(pdf_file)] = result
            
            # Print sample fields
            print(f"\n   📋 Sample fields from {pdf_file.name}:")
            for i, (field_name, field_info) in enumerate(result['fields'].items()):
                if i < 5:  # Show first 5 fields
                    print(f"      • {field_name} ({field_info['type']})")
                elif i == 5:
                    print(f"      ... and {len(result['fields']) - 5} more")
                    break
    
    # Save comprehensive mapping
    if all_results:
        scanner.save_mapping(all_results, 'comprehensive_field_mapping.json')
        print(f"\n✅ Scanned {len(all_results)} PDFs successfully")
        print("📁 Results saved to comprehensive_field_mapping.json")

if __name__ == "__main__":
    main()