#!/usr/bin/env python3
"""
Investigate what actually happened when creating the clean template
Check if original form fields still exist but are hidden/shrunk
"""

import fitz  # pymupdf
import os

class TemplateInvestigator:
    def __init__(self):
        self.original_template = "documents/California_Residential_Purchase_Agreement_CLEAN_TEMPLATE.pdf"
        self.my_clean_template = "output/CRPA_CLEAN_TEMPLATE.pdf"
        self.template_with_fields = "output/CRPA_TEMPLATE_WITH_FIELDS.pdf"
        
    def investigate_original_template(self):
        """Check what's actually in the original template"""
        print("🔍 INVESTIGATING ORIGINAL TEMPLATE")
        print("=" * 60)
        
        doc = fitz.open(self.original_template)
        
        total_widgets = 0
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            if widgets:
                print(f"📄 Page {page_num + 1}: {len(widgets)} widgets found")
                total_widgets += len(widgets)
                
                for i, widget in enumerate(widgets[:5]):  # Show first 5 widgets
                    print(f"  Widget {i+1}:")
                    print(f"    Name: {widget.field_name}")
                    print(f"    Type: {widget.field_type}")
                    print(f"    Value: {widget.field_value}")
                    print(f"    Rect: {widget.rect}")
                    print()
        
        print(f"🎯 TOTAL WIDGETS IN ORIGINAL: {total_widgets}")
        doc.close()
        
        return total_widgets > 0
    
    def investigate_my_clean_template(self):
        """Check what's in my 'clean' template"""
        print(f"\n🔍 INVESTIGATING MY 'CLEAN' TEMPLATE")
        print("=" * 60)
        
        doc = fitz.open(self.my_clean_template)
        
        total_widgets = 0
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            if widgets:
                print(f"📄 Page {page_num + 1}: {len(widgets)} widgets found")
                total_widgets += len(widgets)
                
                for i, widget in enumerate(widgets[:5]):  # Show first 5 widgets
                    print(f"  Widget {i+1}:")
                    print(f"    Name: {widget.field_name}")
                    print(f"    Type: {widget.field_type}")
                    print(f"    Value: {widget.field_value}")
                    print(f"    Rect: {widget.rect}")
                    print()
        
        print(f"🎯 TOTAL WIDGETS IN MY CLEAN TEMPLATE: {total_widgets}")
        doc.close()
        
        return total_widgets > 0
    
    def investigate_template_with_fields(self):
        """Check what's in the template with added fields"""
        print(f"\n🔍 INVESTIGATING TEMPLATE WITH ADDED FIELDS")
        print("=" * 60)
        
        doc = fitz.open(self.template_with_fields)
        
        total_widgets = 0
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            if widgets:
                print(f"📄 Page {page_num + 1}: {len(widgets)} widgets found")
                total_widgets += len(widgets)
                
                for i, widget in enumerate(widgets):
                    print(f"  Widget {i+1}:")
                    print(f"    Name: {widget.field_name}")
                    print(f"    Type: {widget.field_type}")
                    print(f"    Value: {widget.field_value}")
                    print(f"    Rect: {widget.rect}")
                    print()
        
        print(f"🎯 TOTAL WIDGETS IN TEMPLATE WITH FIELDS: {total_widgets}")
        doc.close()
        
        return total_widgets > 0
    
    def fix_by_editing_existing_fields(self):
        """If original fields exist, try editing them directly instead of adding new ones"""
        print(f"\n🔧 ATTEMPTING TO EDIT EXISTING FIELDS DIRECTLY")
        print("=" * 60)
        
        # Open the original template (which has the original fields)
        doc = fitz.open(self.original_template)
        
        # Sample CRM data
        crm_data = {
            'buyer_name': 'John & Jane Smith',
            'property_address': '1234 Dream Avenue',
            'city': 'Beverly Hills',
            'state': 'CA',
            'zip_code': '90210',
            'purchase_price': '$2,500,000.00',
            'form_date': '2025-06-01'
        }
        
        # Find fields that might match our data
        field_mappings = {}
        edited_fields = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            
            for widget in widgets:
                field_name = widget.field_name.lower() if widget.field_name else ""
                field_value = widget.field_value or ""
                
                # Try to identify what this field is based on current value or name
                if any(name in field_value.lower() for name in ['benjamin', 'brown', 'hicks']):
                    widget.field_value = crm_data['buyer_name']
                    print(f"  ✓ Updated buyer name field: {widget.field_name}")
                    edited_fields += 1
                elif '13190' in field_value or 'slate creek' in field_value.lower():
                    widget.field_value = crm_data['property_address'] 
                    print(f"  ✓ Updated property address field: {widget.field_name}")
                    edited_fields += 1
                elif 'nevada city' in field_value.lower():
                    widget.field_value = crm_data['city']
                    print(f"  ✓ Updated city field: {widget.field_name}")
                    edited_fields += 1
                elif field_value == 'Nevada' or field_value == 'CA':
                    widget.field_value = crm_data['state']
                    print(f"  ✓ Updated state field: {widget.field_name}")
                    edited_fields += 1
                elif '95959' in field_value or '92101' in field_value:
                    widget.field_value = crm_data['zip_code']
                    print(f"  ✓ Updated zip field: {widget.field_name}")
                    edited_fields += 1
                elif '930,000' in field_value or '750,000' in field_value:
                    widget.field_value = crm_data['purchase_price']
                    print(f"  ✓ Updated purchase price field: {widget.field_name}")
                    edited_fields += 1
                elif 'april 7, 2025' in field_value.lower():
                    widget.field_value = crm_data['form_date']
                    print(f"  ✓ Updated date field: {widget.field_name}")
                    edited_fields += 1
                
                widget.update()
        
        # Save the properly edited form
        output_path = "output/CRPA_PROPERLY_EDITED.pdf"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)
        doc.close()
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"\n✅ PROPERLY EDITED FORM CREATED!")
            print(f"📁 File: {output_path}")
            print(f"📊 Size: {file_size:,} bytes")
            print(f"✏️ Edited {edited_fields} existing fields")
            print(f"🌐 Windows path: \\\\wsl.localhost\\Ubuntu\\home\\ender\\.claude\\projects\\offer-creator\\{output_path}")
            print(f"🎯 This should work with existing form structure!")
            
            return output_path
        else:
            print("❌ Failed to create properly edited form")
            return None

def main():
    """Investigate what went wrong and try to fix it"""
    investigator = TemplateInvestigator()
    
    print("🕵️ TEMPLATE INVESTIGATION")
    print("Figuring out what actually happened...")
    print("=" * 80)
    
    # Check all templates
    original_has_fields = investigator.investigate_original_template()
    clean_has_fields = investigator.investigate_my_clean_template()  
    added_fields_count = investigator.investigate_template_with_fields()
    
    print(f"\n📊 INVESTIGATION SUMMARY:")
    print(f"  Original template has fields: {original_has_fields}")
    print(f"  My 'clean' template has fields: {clean_has_fields}")
    print(f"  Added fields template has widgets: {added_fields_count}")
    
    if original_has_fields:
        print(f"\n💡 AHA! The original template ALREADY has form fields!")
        print(f"🎯 Solution: Edit existing fields instead of adding new ones")
        
        # Try fixing by editing existing fields
        result = investigator.fix_by_editing_existing_fields()
        
        if result:
            print(f"\n🎉 POTENTIAL FIX CREATED!")
            print(f"Try opening: {result}")

if __name__ == "__main__":
    main()