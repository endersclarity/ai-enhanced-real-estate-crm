#!/usr/bin/env python3

# Fix the old PyPDF2 code to work with new version
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import BooleanObject, IndirectObject, NameObject
import os

def manual_pdf_fill_test():
    """Manual test to show the field matching failure"""
    
    print("🔍 TESTING FIELD MATCHING FAILURE...")
    
    # Step 1: Load CSV
    print("\n1️⃣ Loading CSV data:")
    df = pd.read_csv('/home/ender/.claude/test_data.csv')
    print(f"   CSV columns: {list(df.columns)}")
    row_data = df.iloc[0].to_dict()  # First row
    print(f"   First row data: {row_data}")
    
    # Step 2: Check PDF fields
    print("\n2️⃣ Checking PDF fields:")
    reader = PdfReader('/home/ender/.claude/test_form.pdf')
    fields = reader.get_fields()
    if fields:
        print(f"   PDF has {len(fields)} fields:")
        for i, field_name in enumerate(list(fields.keys())[:8]):
            print(f"     - {field_name}")
        if len(fields) > 8:
            print(f"     ... and {len(fields)-8} more")
    else:
        print("   No fillable fields found!")
        return
    
    # Step 3: Try to match fields
    print("\n3️⃣ Attempting field matching:")
    csv_fields = set(row_data.keys())
    pdf_fields = set(fields.keys())
    matches = csv_fields.intersection(pdf_fields)
    print(f"   CSV fields: {csv_fields}")
    print(f"   PDF fields: {list(pdf_fields)[:5]}... (showing first 5)")
    print(f"   Exact matches: {matches}")
    
    if not matches:
        print("   ❌ NO MATCHES FOUND!")
    
    # Step 4: Try to fill anyway
    print("\n4️⃣ Attempting to fill PDF...")
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    
    try:
        # This will silently fail - nothing gets filled
        page = writer.pages[0]
        writer.update_page_form_field_values(page, row_data)
        
        output_path = '/home/ender/.claude/failed_output.pdf'
        with open(output_path, 'wb') as output:
            writer.write(output)
        
        print(f"   ✅ PDF created at: {output_path}")
        print("   📝 But check it - nothing should be filled!")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🎯 CONCLUSION:")
    print("   The tool created a PDF but filled NOTHING because")
    print("   CSV column names don't match PDF field names.")
    print("   This is the exact problem we need to solve!")

if __name__ == "__main__":
    manual_pdf_fill_test()