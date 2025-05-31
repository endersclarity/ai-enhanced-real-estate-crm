#!/usr/bin/env python3

import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import os

def df_csv_to_PDF_fixed(csv_file, pdf_template, output_filename):
    """Fixed version that actually works with modern PyPDF2"""
    
    print(f"🔄 Processing: {csv_file} → {pdf_template}")
    
    # Read CSV
    df = pd.read_csv(csv_file)
    print(f"📊 CSV has {len(df)} rows with columns: {list(df.columns)}")
    
    # Check PDF fields
    reader = PdfReader(pdf_template)
    fields = reader.get_fields()
    
    if not fields:
        print("❌ PDF has no fillable fields!")
        return
    
    print(f"📄 PDF has {len(fields)} fillable fields:")
    for i, field_name in enumerate(list(fields.keys())[:5]):
        print(f"   - {field_name}")
    if len(fields) > 5:
        print(f"   ... and {len(fields)-5} more")
    
    # Create output directory
    output_dir = f"{pdf_template.split('.')[0]}_AUTOFILLOUTPUT"
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each row
    for idx, row in df.iterrows():
        print(f"\n🔄 Processing row {idx+1}...")
        
        # Convert row to dict, remove NaN values
        row_data = {k: v for k, v in row.to_dict().items() if pd.notna(v)}
        print(f"   Data: {row_data}")
        
        # Check for field matches
        csv_fields = set(row_data.keys())
        pdf_fields = set(fields.keys())
        matches = csv_fields.intersection(pdf_fields)
        
        print(f"   🔍 Field matching: {len(matches)} matches found")
        if matches:
            print(f"      Matches: {matches}")
        else:
            print(f"      ❌ NO MATCHES! CSV: {csv_fields}")
            print(f"                      PDF: {list(pdf_fields)[:3]}...")
        
        # Create writer and try to fill
        writer = PdfWriter()
        writer.append_pages_from_reader(reader)
        
        try:
            page = writer.pages[0]
            writer.update_page_form_field_values(page, row_data)
            
            # Save output
            output_path = os.path.join(output_dir, f"{output_filename}_{idx+1}.pdf")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            print(f"   ✅ Saved: {output_path}")
            
        except Exception as e:
            print(f"   ❌ Error filling PDF: {e}")
    
    print(f"\n🎯 COMPLETE! Check {output_dir}/ for results")

if __name__ == "__main__":
    df_csv_to_PDF_fixed(
        'test_data.csv',
        'test_form.pdf', 
        'test_output'
    )