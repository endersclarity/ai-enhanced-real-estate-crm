#!/usr/bin/env python3
"""
Simple CSV to PDF Generator
Read client data from spreadsheet, fill PDF forms
"""

import pandas as pd
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import sys
import os
from datetime import datetime

def read_client_data(csv_file):
    """Read client data from CSV spreadsheet"""
    try:
        df = pd.read_csv(csv_file)
        return df
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

def generate_pdf_from_template(client_data, template_pdf, output_pdf):
    """Fill PDF template with client data"""
    try:
        # Read template PDF
        with open(template_pdf, 'rb') as template_file:
            reader = PyPDF2.PdfReader(template_file)
            
            # Handle password protection
            if reader.is_encrypted:
                reader.decrypt('')  # Empty password for ZipForm Plus files
            
            writer = PyPDF2.PdfWriter()
            
            # Get form fields (if any)
            if reader.pages[0].get('/Annots'):
                print(f"Form has fillable fields - attempting to populate")
                # TODO: Map client_data to form fields
            else:
                print(f"No fillable fields found - creating overlay")
                # Create text overlay instead
                
            # Copy pages
            for page in reader.pages:
                writer.add_page(page)
            
            # Write output
            with open(output_pdf, 'wb') as output_file:
                writer.write(output_file)
                
        return True
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return False

def main():
    csv_file = "simple_client_spreadsheet.csv"
    
    if not os.path.exists(csv_file):
        print(f"CSV file not found: {csv_file}")
        print("Create your client data in Excel/Google Sheets and save as CSV")
        return
    
    # Read client data
    df = read_client_data(csv_file)
    if df is None:
        return
    
    print(f"Found {len(df)} clients in spreadsheet")
    
    # List available PDF templates
    pdf_templates = [f for f in os.listdir('.') if f.endswith('.pdf') and 'California' in f]
    
    if not pdf_templates:
        print("No PDF templates found")
        return
    
    print(f"Available templates: {pdf_templates}")
    
    # Generate PDFs for each client
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"simple_generated_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    for index, client in df.iterrows():
        client_name = f"{client['Buyer_First_Name']}_{client['Buyer_Last_Name']}"
        
        for template in pdf_templates:
            output_file = f"{output_dir}/{client_name}_{template}"
            
            success = generate_pdf_from_template(client, template, output_file)
            if success:
                print(f"✓ Generated: {output_file}")
            else:
                print(f"✗ Failed: {output_file}")

if __name__ == "__main__":
    main()