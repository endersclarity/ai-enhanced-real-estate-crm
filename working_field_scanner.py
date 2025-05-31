#!/usr/bin/env python3
"""
Working PDF Field Scanner - Extract form fields using correct API calls
"""

import PyPDF2
import json
import re
from pathlib import Path

class WorkingFieldScanner:
    def __init__(self):
        self.field_mappings = {}
    
    def scan_with_pypdf2(self, pdf_path):
        """Extract form fields using PyPDF2 correct API"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                fields = {}
                
                # Check if PDF has form fields
                if hasattr(reader, 'get_fields') and reader.get_fields():
                    for field_name, field_obj in reader.get_fields().items():
                        fields[field_name] = {
                            'type': str(field_obj.get('/FT', 'text')),
                            'value': str(field_obj.get('/V', '')),
                            'rect': str(field_obj.get('/Rect', ''))
                        }
                
                # Alternative: scan each page for annotations
                if not fields:
                    for page_num, page in enumerate(reader.pages):
                        if '/Annots' in page:
                            annotations = page['/Annots']
                            for annot in annotations:
                                annot_obj = annot.get_object()
                                if '/T' in annot_obj:  # Field name
                                    field_name = str(annot_obj['/T'])
                                    fields[field_name] = {
                                        'type': str(annot_obj.get('/FT', 'text')),
                                        'value': str(annot_obj.get('/V', '')),
                                        'page': page_num
                                    }
                
                return fields
                
        except Exception as e:
            print(f"PyPDF2 error: {e}")
            return {}
    
    def scan_with_pdfplumber(self, pdf_path):
        """Extract text fields using pdfplumber for non-form PDFs"""
        try:
            import pdfplumber
            
            text_content = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text_content += page.extract_text() or ""
            
            # Look for patterns that suggest form fields
            potential_fields = self.extract_field_patterns(text_content)
            return potential_fields
            
        except Exception as e:
            print(f"pdfplumber error: {e}")
            return {}
    
    def extract_field_patterns(self, text):
        """Extract potential form field patterns from text"""
        fields = {}
        
        # Common patterns for form fields
        patterns = [
            r'(\w+\s*\w*)\s*:?\s*_+',  # Name: ____
            r'(\w+\s*\w*)\s*\[\s*\]',   # Name [ ]
            r'(\w+\s*\w*)\s*\(\s*\)',   # Name ( )
            r'Date:\s*_+',              # Date: ____
            r'Price:\s*\$?_+',          # Price: $____
            r'Address:\s*_+',           # Address: ____
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    field_name = match[0]
                else:
                    field_name = match
                
                clean_name = field_name.strip()
                if len(clean_name) > 2:  # Avoid single letters
                    fields[clean_name] = {
                        'type': 'text',
                        'value': '',
                        'source': 'text_pattern'
                    }
        
        return fields
    
    def create_csv_mapping(self, fields):
        """Create CSV column mapping from field names"""
        mapping = {}
        
        for field_name in fields.keys():
            csv_column = self.normalize_field_name(field_name)
            mapping[csv_column] = field_name
            
        return mapping
    
    def normalize_field_name(self, field_name):
        """Convert field name to CSV column"""
        normalized = field_name.lower().strip()
        
        # Replace spaces and special chars
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', '_', normalized)
        
        # Smart mapping
        smart_mappings = {
            'buyer_name': 'buyer_name',
            'buyer_first_name': 'buyer_first_name',
            'buyer_last_name': 'buyer_last_name',
            'purchase_price': 'purchase_price',
            'sale_price': 'purchase_price',
            'property_address': 'property_address',
            'address': 'property_address',
            'earnest_money': 'earnest_money',
            'deposit': 'earnest_money',
            'agent_name': 'agent_name',
            'agent': 'agent_name',
            'date': 'date',
            'closing_date': 'closing_date'
        }
        
        return smart_mappings.get(normalized, normalized)
    
    def scan_pdf(self, pdf_path):
        """Main scanning function"""
        print(f"\n🔍 Scanning: {Path(pdf_path).name}")
        
        # Try form fields first
        fields = self.scan_with_pypdf2(pdf_path)
        
        if not fields:
            # Try text pattern extraction
            fields = self.scan_with_pdfplumber(pdf_path)
        
        if fields:
            print(f"   ✅ Found {len(fields)} potential fields")
            csv_mapping = self.create_csv_mapping(fields)
            
            return {
                'file': str(pdf_path),
                'fields': fields,
                'csv_mapping': csv_mapping,
                'field_count': len(fields)
            }
        else:
            print("   ❌ No fields found")
            return None

def main():
    scanner = WorkingFieldScanner()
    
    # Test with a few key PDFs
    test_files = [
        'California_Residential_Purchase_Agreement_-_1224_ts77432.pdf',
        'Buyer_Representation_and_Broker_Compensation_Agreement_-_1224_ts74307.pdf',
        'Statewide_Buyer_and_Seller_Advisory_-_624_ts89932.pdf'
    ]
    
    results = {}
    
    for pdf_file in test_files:
        if Path(pdf_file).exists():
            result = scanner.scan_pdf(pdf_file)
            if result:
                results[pdf_file] = result
                
                # Show sample fields
                print(f"   📋 Sample fields:")
                for i, (field_name, field_info) in enumerate(result['fields'].items()):
                    if i < 5:
                        print(f"      • {field_name}")
                    elif i == 5:
                        print(f"      ... and {len(result['fields']) - 5} more")
                        break
    
    if results:
        # Save results
        with open('field_scan_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Scanned {len(results)} PDFs")
        print("💾 Results saved to field_scan_results.json")
        
        # Create simple CSV template
        all_fields = set()
        for result in results.values():
            all_fields.update(result['csv_mapping'].keys())
        
        csv_template = ','.join(sorted(all_fields))
        with open('auto_generated_csv_template.csv', 'w') as f:
            f.write(csv_template + '\n')
        
        print("📝 CSV template saved to auto_generated_csv_template.csv")
    else:
        print("\n❌ No fields found in any PDFs")

if __name__ == "__main__":
    main()