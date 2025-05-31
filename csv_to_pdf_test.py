#!/usr/bin/env python3
"""
CSV to PDF Form Field Population Test
Tests direct field population from CSV data using PyMuPDF
"""

import fitz  # PyMuPDF
import csv
import json
from datetime import datetime

def load_csv_row(csv_file, row_number=0):
    """Load specific row from CSV file"""
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader):
                if i == row_number:
                    return row
        return None
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def map_csv_to_pdf_fields(csv_data):
    """Map CSV fields to common PDF field names"""
    # Based on activeContext.md noting 104 form fields detected earlier
    field_mapping = {
        # Buyer information
        "Buyer": csv_data.get('buyer_name', ''),
        "Buyer Name": csv_data.get('buyer_name', ''),
        "Buyer_Name": csv_data.get('buyer_name', ''),
        "Purchaser": csv_data.get('buyer_name', ''),
        "Buyer Phone": csv_data.get('buyer_phone', ''),
        "Buyer_Phone": csv_data.get('buyer_phone', ''),
        "Phone": csv_data.get('buyer_phone', ''),
        "Buyer Email": csv_data.get('buyer_email', ''),
        "Email": csv_data.get('buyer_email', ''),
        "Buyer_Email": csv_data.get('buyer_email', ''),
        
        # Property information
        "Property Address": csv_data.get('property_address', ''),
        "Property_Address": csv_data.get('property_address', ''),
        "Address": csv_data.get('property_address', ''),
        "Subject Property": csv_data.get('property_address', ''),
        
        # Financial information
        "Purchase Price": csv_data.get('offer_price', ''),
        "Purchase_Price": csv_data.get('offer_price', ''),
        "Offer Price": csv_data.get('offer_price', ''),
        "Sale Price": csv_data.get('offer_price', ''),
        "Price": csv_data.get('offer_price', ''),
        "Earnest Money": csv_data.get('earnest_money', ''),
        "Earnest_Money": csv_data.get('earnest_money', ''),
        "Deposit": csv_data.get('earnest_money', ''),
        "Initial Deposit": csv_data.get('earnest_money', ''),
        
        # Dates and terms
        "Offer Date": csv_data.get('offer_date', ''),
        "Date": csv_data.get('offer_date', ''),
        "Escrow Days": csv_data.get('escrow_days', ''),
        "Escrow Period": csv_data.get('escrow_days', ''),
        "Close of Escrow": csv_data.get('escrow_days', ''),
        
        # Agent information  
        "Agent": csv_data.get('agent_name', ''),
        "Agent Name": csv_data.get('agent_name', ''),
        "Broker": csv_data.get('agent_name', ''),
        "Listing Agent": csv_data.get('agent_name', ''),
        "Selling Agent": csv_data.get('agent_name', ''),
        
        # Boolean/checkbox fields
        "Seller Pays Broker": "YES" if csv_data.get('seller_pays_broker') == 'TRUE' else "NO",
        "Septic": "YES" if csv_data.get('has_septic') == 'TRUE' else "NO", 
        "Well": "YES" if csv_data.get('has_well') == 'TRUE' else "NO",
        
        # Additional items
        "Included Items": csv_data.get('included_items', ''),
        "Personal Property": csv_data.get('included_items', ''),
    }
    
    return field_mapping

def fill_pdf_from_csv(pdf_template, csv_file, output_file, row_number=0):
    """Fill PDF form fields from CSV data"""
    print(f"🏠 CSV TO PDF FIELD POPULATION TEST")
    print("=" * 50)
    
    # Load CSV data
    csv_data = load_csv_row(csv_file, row_number)
    if not csv_data:
        print(f"❌ Failed to load row {row_number} from {csv_file}")
        return False
    
    print(f"✅ Loaded CSV row {row_number}: {csv_data['buyer_name']}")
    
    # Map CSV to PDF fields
    field_data = map_csv_to_pdf_fields(csv_data)
    print(f"✅ Mapped {len(field_data)} field values")
    
    try:
        # Open PDF
        doc = fitz.open(pdf_template)
        print(f"✅ Opened PDF: {len(doc)} pages")
        
        total_fields = 0
        filled_fields = 0
        
        # Process each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            
            if widgets:
                print(f"\n📄 Page {page_num + 1}: {len(widgets)} form fields")
                
                for widget in widgets:
                    total_fields += 1
                    field_name = widget.field_name
                    
                    # Try to find matching data
                    if field_name in field_data and field_data[field_name]:
                        try:
                            old_value = widget.field_value
                            widget.field_value = str(field_data[field_name])
                            widget.update()
                            filled_fields += 1
                            print(f"   ✅ {field_name}: '{old_value}' → '{field_data[field_name]}'")
                        except Exception as e:
                            print(f"   ❌ Failed to fill {field_name}: {e}")
                    else:
                        # Try partial matching for field names
                        for mapped_name, value in field_data.items():
                            if mapped_name.lower() in field_name.lower() or field_name.lower() in mapped_name.lower():
                                if value:
                                    try:
                                        widget.field_value = str(value)
                                        widget.update()
                                        filled_fields += 1
                                        print(f"   ✅ {field_name} (partial match): → '{value}'")
                                        break
                                    except Exception as e:
                                        print(f"   ❌ Failed partial fill {field_name}: {e}")
        
        # Save filled PDF
        doc.save(output_file)
        doc.close()
        
        # Results
        print(f"\n📊 FILLING RESULTS:")
        print(f"   Total form fields found: {total_fields}")
        print(f"   Successfully filled: {filled_fields}")
        print(f"   Fill rate: {(filled_fields/total_fields*100):.1f}%" if total_fields > 0 else "   Fill rate: 0%")
        print(f"   Output saved: {output_file}")
        
        # Test data summary
        print(f"\n🎯 FILLED WITH DATA:")
        key_data = ['buyer_name', 'property_address', 'offer_price', 'earnest_money']
        for key in key_data:
            print(f"   {key}: {csv_data.get(key, 'MISSING')}")
        
        return filled_fields > 0
        
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        return False

def test_multiple_clients():
    """Test with multiple client records"""
    print(f"\n🔄 TESTING MULTIPLE CLIENTS")
    print("=" * 30)
    
    # Test first 3 clients
    for i in range(3):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"filled_offer_client_{i+1}_{timestamp}.pdf"
        
        print(f"\n🏠 Testing Client {i+1}:")
        success = fill_pdf_from_csv(
            "California_RPA_Template_Fillable.pdf",
            "sample_clients.csv", 
            output_file,
            row_number=i
        )
        
        if success:
            print(f"✅ Client {i+1} offer generated: {output_file}")
        else:
            print(f"❌ Client {i+1} failed")

if __name__ == "__main__":
    # Test with first client
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"csv_filled_offer_{timestamp}.pdf"
    
    success = fill_pdf_from_csv(
        "California_RPA_Template_Fillable.pdf",
        "sample_clients.csv",
        output_file,
        row_number=0  # John & Jane Smith
    )
    
    if success:
        print(f"\n🎉 SUCCESS! Generated PDF with real client data!")
        print(f"📁 Check file: {output_file}")
        
        # Test multiple clients
        test_multiple_clients()
    else:
        print(f"\n❌ FAILED to generate PDF from CSV")
        
    print(f"\n🔍 Next: Open the generated PDF(s) to verify field population worked!")