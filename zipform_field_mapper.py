#!/usr/bin/env python3
"""
ZipForm Plus Field Mapper
Maps CSV data to specific form fields in flattened PDFs
"""

import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black
from PyPDF2 import PdfReader, PdfWriter
import io
import json
from pathlib import Path

class ZipFormFieldMapper:
    def __init__(self):
        # Field mappings based on the RPA form structure
        # Format: 'csv_column': {'page': page_num, 'x': x_coord, 'y': y_coord, 'font_size': size}
        self.field_mappings = {
            # Page 1 - Basic Info
            'date_prepared': {'page': 1, 'x': 600, 'y': 750, 'font_size': 10},
            'buyer_name': {'page': 1, 'x': 300, 'y': 720, 'font_size': 10},
            'property_address': {'page': 1, 'x': 250, 'y': 690, 'font_size': 10},
            'property_city': {'page': 1, 'x': 200, 'y': 665, 'font_size': 10},
            'property_county': {'page': 1, 'x': 350, 'y': 665, 'font_size': 10},
            'property_zip': {'page': 1, 'x': 500, 'y': 665, 'font_size': 10},
            'apn': {'page': 1, 'x': 300, 'y': 640, 'font_size': 10},
            'purchase_price': {'page': 1, 'x': 350, 'y': 400, 'font_size': 12},
            'coe_days': {'page': 1, 'x': 450, 'y': 375, 'font_size': 10},
            'initial_deposit': {'page': 1, 'x': 350, 'y': 350, 'font_size': 10},
            'loan_amount': {'page': 1, 'x': 350, 'y': 320, 'font_size': 10},
            'down_payment': {'page': 1, 'x': 350, 'y': 290, 'font_size': 10},
            
            # Seller/Buyer Info
            'seller_name': {'page': 18, 'x': 300, 'y': 400, 'font_size': 10},
            'buyer_signature_date': {'page': 17, 'x': 500, 'y': 200, 'font_size': 10},
            'seller_signature_date': {'page': 18, 'x': 500, 'y': 200, 'font_size': 10},
            
            # Agent Information
            'buyer_agent': {'page': 19, 'x': 300, 'y': 600, 'font_size': 10},
            'buyer_brokerage': {'page': 19, 'x': 300, 'y': 580, 'font_size': 10},
            'seller_agent': {'page': 19, 'x': 300, 'y': 500, 'font_size': 10},
            'seller_brokerage': {'page': 19, 'x': 300, 'y': 480, 'font_size': 10},
        }
        
        # Checkbox mappings for Yes/No fields
        self.checkbox_mappings = {
            'all_cash': {'page': 1, 'x': 550, 'y': 400},
            'fha_loan': {'page': 1, 'x': 450, 'y': 320},
            'conventional_loan': {'page': 1, 'x': 350, 'y': 320},
        }

    def load_csv_data(self, csv_path):
        """Load and return CSV data"""
        return pd.read_csv(csv_path)

    def create_overlay(self, data_row):
        """Create a PDF overlay with the populated data"""
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        
        # Populate text fields
        for csv_field, field_info in self.field_mappings.items():
            if csv_field in data_row and pd.notna(data_row[csv_field]):
                can.setFont("Helvetica", field_info['font_size'])
                can.setFillColor(black)
                
                # Convert value to string and handle formatting
                value = str(data_row[csv_field])
                if csv_field == 'purchase_price':
                    try:
                        num_value = float(value)
                        value = f"${num_value:,.0f}"
                    except:
                        value = f"${value}"
                elif 'date' in csv_field.lower():
                    # Format dates consistently
                    value = self.format_date(value)
                
                can.drawString(field_info['x'], field_info['y'], value)
        
        # Handle checkboxes
        for csv_field, checkbox_info in self.checkbox_mappings.items():
            if csv_field in data_row and str(data_row[csv_field]).upper() in ['YES', 'TRUE', '1', 'X']:
                can.setFont("Helvetica", 12)
                can.drawString(checkbox_info['x'], checkbox_info['y'], "X")
        
        can.save()
        packet.seek(0)
        return packet

    def format_date(self, date_str):
        """Format date strings consistently"""
        try:
            # Try to parse and reformat date
            from datetime import datetime
            dt = pd.to_datetime(date_str)
            return dt.strftime("%m/%d/%Y")
        except:
            return str(date_str)

    def populate_pdf(self, template_pdf_path, csv_path, output_dir):
        """Main function to populate PDFs from CSV data"""
        # Load CSV data
        df = self.load_csv_data(csv_path)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        populated_files = []
        
        for index, row in df.iterrows():
            try:
                # Create overlay with data
                overlay_packet = self.create_overlay(row)
                overlay_pdf = PdfReader(overlay_packet)
                
                # Read template PDF
                template_pdf = PdfReader(template_pdf_path)
                output_pdf = PdfWriter()
                
                # Merge overlay with each page
                for page_num in range(len(template_pdf.pages)):
                    page = template_pdf.pages[page_num]
                    
                    # If we have overlay content for this page, merge it
                    if page_num < len(overlay_pdf.pages):
                        page.merge_page(overlay_pdf.pages[page_num])
                    
                    output_pdf.add_page(page)
                
                # Generate output filename
                buyer_name = str(row.get('buyer_name', f'Contract_{index+1}')).replace(' ', '_')
                output_file = output_path / f"{buyer_name}_RPA.pdf"
                
                # Write populated PDF
                with open(output_file, 'wb') as output_stream:
                    output_pdf.write(output_stream)
                
                populated_files.append(str(output_file))
                print(f"✓ Created: {output_file}")
                
            except Exception as e:
                print(f"✗ Error processing row {index}: {e}")
                continue
        
        return populated_files

    def create_sample_csv(self, output_path="sample_zipform_data.csv"):
        """Create a sample CSV with the expected column structure"""
        sample_data = {
            'date_prepared': ['05/28/2025', '05/29/2025'],
            'buyer_name': ['John Smith', 'Jane Doe'],
            'property_address': ['123 Main St', '456 Oak Ave'],
            'property_city': ['Sacramento', 'San Francisco'],
            'property_county': ['Sacramento', 'San Francisco'],
            'property_zip': ['95814', '94102'],
            'apn': ['123-456-789', '987-654-321'],
            'purchase_price': ['450000', '675000'],
            'coe_days': ['30', '45'],
            'initial_deposit': ['5000', '7500'],
            'loan_amount': ['360000', '540000'],
            'down_payment': ['90000', '135000'],
            'seller_name': ['ABC Properties LLC', 'XYZ Investments'],
            'buyer_signature_date': ['05/28/2025', '05/29/2025'],
            'seller_signature_date': ['05/28/2025', '05/29/2025'],
            'buyer_agent': ['John Agent', 'Mary Agent'],
            'buyer_brokerage': ['Best Realty', 'Top Properties'],
            'seller_agent': ['Bob Seller', 'Sue Listing'],
            'seller_brokerage': ['Prime Real Estate', 'Elite Properties'],
            'all_cash': ['No', 'No'],
            'fha_loan': ['No', 'Yes'],
            'conventional_loan': ['Yes', 'No'],
        }
        
        df = pd.DataFrame(sample_data)
        df.to_csv(output_path, index=False)
        print(f"Sample CSV created: {output_path}")
        return output_path

def main():
    mapper = ZipFormFieldMapper()
    
    # Create sample CSV
    csv_file = mapper.create_sample_csv()
    
    # Instructions for user
    print("\n" + "="*60)
    print("ZIPFORM FIELD MAPPER - SETUP COMPLETE")
    print("="*60)
    print("1. Place your flattened RPA PDF in this directory as 'template.pdf'")
    print("2. Edit the sample CSV file with your data:")
    print(f"   - {csv_file}")
    print("3. Run the population:")
    print("   mapper.populate_pdf('template.pdf', 'sample_zipform_data.csv', 'output')")
    print("\nTo customize field positions:")
    print("- Edit the field_mappings dictionary in the ZipFormFieldMapper class")
    print("- Adjust x,y coordinates based on your PDF layout")
    print("="*60)

if __name__ == "__main__":
    main()