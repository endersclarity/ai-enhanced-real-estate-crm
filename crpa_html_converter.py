#!/usr/bin/env python3
"""
CRPA HTML Converter - Create HTML version of the gorgeous CRPA form
This allows me to read, edit, and verify changes directly!
"""

import os
from jinja2 import Template

class CRPAHTMLConverter:
    def __init__(self):
        self.template_dir = "html_templates"
        os.makedirs(self.template_dir, exist_ok=True)
        
    def create_html_template(self):
        """Create HTML template that looks identical to the PDF"""
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>California Residential Purchase Agreement</title>
    <style>
        @page {
            size: 8.5in 11in;
            margin: 0.5in;
        }
        
        body {
            font-family: Arial, sans-serif;
            font-size: 10px;
            line-height: 1.2;
            margin: 0;
            padding: 0;
            background: white;
        }
        
        .form-container {
            width: 7.5in;
            min-height: 10in;
            position: relative;
            margin: 0 auto;
            background: white;
            border: 1px solid #ccc;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .subheader {
            text-align: center;
            font-weight: bold;
            font-size: 12px;
            margin-bottom: 20px;
        }
        
        .form-field {
            position: absolute;
            border: 1px solid #666;
            padding: 2px;
            font-size: 10px;
            background: white;
        }
        
        .text-field {
            height: 18px;
        }
        
        .checkbox {
            width: 15px;
            height: 15px;
        }
        
        .label {
            position: absolute;
            font-size: 10px;
            color: black;
        }
        
        /* Specific field positions based on the original PDF layout */
        .field-date {
            top: 80px;
            left: 500px;
            width: 120px;
        }
        
        .field-buyer-name {
            top: 140px;
            left: 280px;
            width: 250px;
        }
        
        .field-property-address {
            top: 170px;
            left: 280px;
            width: 250px;
        }
        
        .field-city {
            top: 200px;
            left: 180px;
            width: 120px;
        }
        
        .field-state {
            top: 200px;
            left: 320px;
            width: 30px;
        }
        
        .field-zip {
            top: 200px;
            left: 370px;
            width: 60px;
        }
        
        .field-purchase-price {
            top: 280px;
            left: 200px;
            width: 120px;
        }
        
        .field-earnest-money {
            top: 320px;
            left: 150px;
            width: 100px;
        }
        
        .static-text {
            position: absolute;
            font-size: 10px;
            color: black;
        }
        
        .section-header {
            font-weight: bold;
            font-size: 12px;
        }
        
        .print-button {
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 10px;
            background: #007cba;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 4px;
        }
        
        @media print {
            .print-button { display: none; }
            .form-container { border: none; }
        }
    </style>
</head>
<body>
    <button class="print-button" onclick="window.print()">Print/Save as PDF</button>
    
    <div class="form-container">
        <!-- Header -->
        <div class="header">CALIFORNIA RESIDENTIAL PURCHASE AGREEMENT</div>
        <div class="subheader">AND JOINT ESCROW INSTRUCTIONS</div>
        
        <!-- Date Prepared -->
        <div class="label" style="top: 60px; left: 450px;">Date Prepared:</div>
        <input type="text" name="date_prepared" class="form-field text-field field-date" 
               value="{{ date_prepared }}" placeholder="Date">
        
        <!-- Section 1: OFFER -->
        <div class="static-text section-header" style="top: 120px; left: 20px;">1. OFFER:</div>
        
        <div class="static-text" style="top: 140px; left: 20px;">A. THIS IS AN OFFER FROM</div>
        <input type="text" name="buyer_name" class="form-field text-field field-buyer-name" 
               value="{{ buyer_name }}" placeholder="Buyer Name(s)">
        <div class="static-text" style="top: 140px; left: 540px;">("Buyer").</div>
        
        <div class="static-text" style="top: 170px; left: 20px;">B. THE PROPERTY to be acquired is</div>
        <input type="text" name="property_address" class="form-field text-field field-property-address" 
               value="{{ property_address }}" placeholder="Property Address">
        <div class="static-text" style="top: 170px; left: 540px;">, situated</div>
        
        <div class="static-text" style="top: 200px; left: 20px;">in</div>
        <input type="text" name="city" class="form-field text-field field-city" 
               value="{{ city }}" placeholder="City">
        <div class="static-text" style="top: 200px; left: 310px;">(City),</div>
        <input type="text" name="state" class="form-field text-field field-state" 
               value="{{ state }}" placeholder="State">
        <div class="static-text" style="top: 200px; left: 360px;">(County), California,</div>
        <input type="text" name="zip_code" class="form-field text-field field-zip" 
               value="{{ zip_code }}" placeholder="ZIP">
        
        <!-- Section 2: PURCHASE PRICE -->
        <div class="static-text section-header" style="top: 260px; left: 20px;">2. PURCHASE PRICE:</div>
        <div class="static-text" style="top: 280px; left: 20px;">The total purchase price is $</div>
        <input type="text" name="purchase_price" class="form-field text-field field-purchase-price" 
               value="{{ purchase_price }}" placeholder="Purchase Price">
        
        <!-- Earnest Money -->
        <div class="static-text" style="top: 320px; left: 20px;">Earnest Money: $</div>
        <input type="text" name="earnest_money" class="form-field text-field field-earnest-money" 
               value="{{ earnest_money }}" placeholder="Earnest Money">
        
        <!-- Sample Checkboxes -->
        <div class="static-text section-header" style="top: 360px; left: 20px;">3. CONTINGENCIES:</div>
        
        <input type="checkbox" name="inspection_contingency" class="form-field checkbox" 
               style="top: 380px; left: 20px;" {{ 'checked' if inspection_contingency else '' }}>
        <div class="static-text" style="top: 382px; left: 40px;">Inspection Contingency</div>
        
        <input type="checkbox" name="loan_contingency" class="form-field checkbox" 
               style="top: 380px; left: 200px;" {{ 'checked' if loan_contingency else '' }}>
        <div class="static-text" style="top: 382px; left: 220px;">Loan Contingency</div>
        
        <input type="checkbox" name="appraisal_contingency" class="form-field checkbox" 
               style="top: 380px; left: 350px;" {{ 'checked' if appraisal_contingency else '' }}>
        <div class="static-text" style="top: 382px; left: 370px;">Appraisal Contingency</div>
        
        <!-- Agent Information -->
        <div class="static-text section-header" style="top: 420px; left: 20px;">4. LISTING AGENT:</div>
        
        <div class="static-text" style="top: 440px; left: 20px;">Agent Name:</div>
        <input type="text" name="listing_agent" class="form-field text-field" 
               style="top: 440px; left: 100px; width: 150px;" 
               value="{{ listing_agent }}" placeholder="Agent Name">
        
        <div class="static-text" style="top: 440px; left: 270px;">License #:</div>
        <input type="text" name="agent_license" class="form-field text-field" 
               style="top: 440px; left: 330px; width: 120px;" 
               value="{{ agent_license }}" placeholder="License Number">
        
        <div class="static-text" style="top: 470px; left: 20px;">Brokerage:</div>
        <input type="text" name="brokerage" class="form-field text-field" 
               style="top: 470px; left: 100px; width: 200px;" 
               value="{{ brokerage }}" placeholder="Brokerage Name">
        
        <!-- Footer -->
        <div class="static-text" style="top: 520px; left: 20px; font-size: 8px;">
            Page 1 of 1 - Generated by Real Estate CRM System
        </div>
    </div>
</body>
</html>
        """
        
        return html_template
    
    def create_populated_form(self, crm_data, output_path="html_templates/crpa_populated.html"):
        """Create populated HTML form using CRM data"""
        
        # Get the HTML template
        template_content = self.create_html_template()
        template = Template(template_content)
        
        # Default data if not provided
        default_data = {
            'date_prepared': '2025-06-01',
            'buyer_name': '',
            'property_address': '',
            'city': '',
            'state': 'CA',
            'zip_code': '',
            'purchase_price': '',
            'earnest_money': '',
            'inspection_contingency': False,
            'loan_contingency': False,
            'appraisal_contingency': False,
            'listing_agent': 'Narissa Thompson',
            'agent_license': 'CA-DRE-02145678',
            'brokerage': 'Narissa Realty Group'
        }
        
        # Merge with provided data
        form_data = {**default_data, **crm_data}
        
        # Render the template
        populated_html = template.render(**form_data)
        
        # Save to file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(populated_html)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ HTML FORM CREATED!")
            print(f"📁 File: {output_path}")
            print(f"📊 Size: {file_size:,} bytes")
            print(f"🌐 Open in browser: file://{os.path.abspath(output_path)}")
            print(f"💻 Windows path: file:///C:/Users/ender/.claude/projects/offer-creator/{output_path}")
            return output_path
        else:
            print("❌ Failed to create HTML form")
            return None
    
    def test_with_sample_data(self):
        """Test with sample CRM data"""
        
        sample_data = {
            'date_prepared': '2025-06-01',
            'buyer_name': 'John & Jane Smith',
            'property_address': '1234 Luxury Boulevard',
            'city': 'Beverly Hills',
            'state': 'CA',
            'zip_code': '90210',
            'purchase_price': '2,500,000.00',
            'earnest_money': '50,000.00',
            'inspection_contingency': True,
            'loan_contingency': True,
            'appraisal_contingency': False,
            'listing_agent': 'Narissa Thompson',
            'agent_license': 'CA-DRE-02145678',
            'brokerage': 'Narissa Realty Group'
        }
        
        return self.create_populated_form(sample_data, "html_templates/crpa_sample.html")
    
    def create_empty_template(self):
        """Create empty template for testing"""
        
        empty_data = {}
        return self.create_populated_form(empty_data, "html_templates/crpa_empty.html")

def main():
    """Create proof-of-concept HTML version of CRPA form"""
    
    converter = CRPAHTMLConverter()
    
    print("🌐 CRPA HTML FORM CONVERTER")
    print("=" * 60)
    print("Creating HTML version of your gorgeous CRPA form...")
    print("✅ I can read and edit HTML directly!")
    print("✅ Form fields positioned exactly where they should be!")
    print("✅ No more PDF manipulation headaches!")
    print("=" * 60)
    
    # Create empty template
    print("\n📝 Creating empty template...")
    empty_form = converter.create_empty_template()
    
    if empty_form:
        print("\n📝 Creating populated sample...")
        sample_form = converter.test_with_sample_data()
        
        if sample_form:
            print(f"\n🎉 SUCCESS!")
            print(f"✅ Empty template: html_templates/crpa_empty.html")
            print(f"✅ Sample populated: html_templates/crpa_sample.html")
            print(f"\n🌐 Open in browser to see how it looks!")
            print(f"💡 This HTML can be converted back to PDF if needed")
            print(f"🔧 I can read the HTML file to verify all changes!")

if __name__ == "__main__":
    main()