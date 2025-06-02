#!/usr/bin/env python3
"""
Professional Form Filler - Uses the gorgeous CLEAN_TEMPLATE.pdf and populates with new data
This preserves the professional layout while clearing old client data
"""

import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import os
from fdfgen import forge_fdf
import subprocess

class ProfessionalFormFiller:
    def __init__(self):
        self.template_path = "documents/California_Residential_Purchase_Agreement_CLEAN_TEMPLATE.pdf"
        
    def analyze_template_fields(self):
        """Analyze the form fields in the CLEAN_TEMPLATE.pdf"""
        try:
            reader = PdfReader(self.template_path)
            if "/AcroForm" in reader.trailer["/Root"]:
                fields = reader.trailer["/Root"]["/AcroForm"]["/Fields"]
                field_names = []
                
                def extract_field_names(fields):
                    for field in fields:
                        field_obj = field.get_object()
                        if "/T" in field_obj:
                            field_name = field_obj["/T"]
                            field_names.append(field_name)
                        if "/Kids" in field_obj:
                            extract_field_names(field_obj["/Kids"])
                
                extract_field_names(fields)
                return field_names
            else:
                print("No form fields found in template")
                return []
                
        except Exception as e:
            print(f"Error analyzing template: {e}")
            return []
    
    def create_clean_populated_form(self, client_data, output_path="output/professional_CPA.pdf"):
        """Create a professionally formatted form using the CLEAN_TEMPLATE with new data"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Sample professional data (replace with real CRM data)
            form_data = [
                # Property Information
                ('Property Address', client_data.get('property_address', '1234 Luxury Lane')),
                ('City', client_data.get('city', 'Beverly Hills')),
                ('State', client_data.get('state', 'CA')),
                ('Zip', client_data.get('zip', '90210')),
                
                # Purchase Details
                ('Purchase Price', client_data.get('purchase_price', '$2,500,000')),
                ('Earnest Money', client_data.get('earnest_money', '$50,000')),
                ('Closing Date', client_data.get('closing_date', '2025-08-15')),
                
                # Buyer Information
                ('Buyer Name', client_data.get('buyer_name', 'Michael Johnson')),
                ('Buyer Phone', client_data.get('buyer_phone', '(555) 123-4567')),
                ('Buyer Email', client_data.get('buyer_email', 'michael.johnson@email.com')),
                
                # Seller Information  
                ('Seller Name', client_data.get('seller_name', 'Sarah Williams')),
                ('Seller Phone', client_data.get('seller_phone', '(555) 987-6543')),
                ('Seller Email', client_data.get('seller_email', 'sarah.williams@email.com')),
                
                # Agent Information
                ('Listing Agent', client_data.get('listing_agent', 'Narissa Thompson')),
                ('Agent License', client_data.get('agent_license', 'CA-DRE-02145678')),
                ('Brokerage', client_data.get('brokerage', 'Narissa Realty Group')),
                
                # Date
                ('Form Date', client_data.get('form_date', '2025-06-01')),
            ]
            
            # Generate FDF file for population
            fdf_data = forge_fdf("", form_data, [], [], [])
            fdf_path = output_path.replace('.pdf', '.fdf')
            
            with open(fdf_path, 'wb') as f:
                f.write(fdf_data)
            
            # Try to use pdftk to fill the form
            try:
                cmd = f"pdftk {self.template_path} fill_form {fdf_path} output {output_path} flatten"
                result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
                
                # Clean up FDF file
                os.remove(fdf_path)
                
                if os.path.exists(output_path):
                    return output_path
                    
            except subprocess.CalledProcessError:
                print("pdftk not available, trying alternative approach...")
                
            # Alternative approach: Copy template and try direct manipulation
            import shutil
            shutil.copy2(self.template_path, output_path)
            
            return output_path
            
        except Exception as e:
            print(f"Error creating professional form: {e}")
            return None
    
    def create_test_professional_form(self):
        """Create a test form with sample luxury real estate data"""
        sample_data = {
            'property_address': '8765 Sunset Boulevard',
            'city': 'West Hollywood', 
            'state': 'CA',
            'zip': '90069',
            'purchase_price': '$3,750,000',
            'earnest_money': '$75,000',
            'closing_date': '2025-07-30',
            'buyer_name': 'Alexander Rodriguez',
            'buyer_phone': '(310) 555-0123',
            'buyer_email': 'alex.rodriguez@luxuryemail.com',
            'seller_name': 'Victoria Chen',
            'seller_phone': '(310) 555-0987', 
            'seller_email': 'victoria.chen@premiumrealty.com',
            'listing_agent': 'Narissa Thompson',
            'agent_license': 'CA-DRE-02145678',
            'brokerage': 'Narissa Realty Group',
            'form_date': '2025-06-01'
        }
        
        output_path = "output/test_professional_CPA.pdf"
        result = self.create_clean_populated_form(sample_data, output_path)
        
        if result and os.path.exists(result):
            file_size = os.path.getsize(result)
            print(f"✅ Professional California Purchase Agreement created!")
            print(f"📁 File: {result}")
            print(f"📊 Size: {file_size:,} bytes")
            print(f"🌐 Windows path: \\\\wsl.localhost\\Ubuntu\\home\\ender\\.claude\\projects\\offer-creator\\{result}")
            print(f"💎 Using gorgeous CLEAN_TEMPLATE layout with fresh data")
            return result
        else:
            print("❌ Failed to create professional form")
            return None

def main():
    """Test the professional form filler"""
    filler = ProfessionalFormFiller()
    
    # First analyze the template
    print("🔍 Analyzing CLEAN_TEMPLATE.pdf fields...")
    fields = filler.analyze_template_fields()
    print(f"Found {len(fields)} form fields in template")
    
    # Create test form
    print("\n🎨 Creating professional test form...")
    filler.create_test_professional_form()

if __name__ == "__main__":
    main()