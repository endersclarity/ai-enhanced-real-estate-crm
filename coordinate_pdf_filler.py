#!/usr/bin/env python3
"""
Coordinate-based PDF Filler - Uses visual field mappings to overlay text
"""

import json
import csv
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

class CoordinatePDFFiller:
    def __init__(self):
        self.mappings = {}
        
    def load_field_mapping(self, mapping_file):
        """Load field mapping from JSON file created by visual mapper"""
        try:
            with open(mapping_file, 'r') as f:
                self.mappings = json.load(f)
            print(f"✅ Loaded mapping with {len(self.mappings.get('fields', []))} fields")
            return True
        except Exception as e:
            print(f"❌ Error loading mapping: {e}")
            return False
    
    def create_overlay_pdf(self, csv_data, mapping, page_size=(612, 792)):
        """Create overlay PDF with text at specified coordinates"""
        # Create a bytes buffer for the overlay PDF
        packet = io.BytesIO()
        overlay_canvas = canvas.Canvas(packet, pagesize=page_size)
        
        # Set font
        overlay_canvas.setFont("Helvetica", 10)
        
        for field in mapping.get('fields', []):
            field_name = field['name']
            coords = field['coordinates']
            
            # Get value from CSV data
            value = csv_data.get(field_name, '')
            
            if value:
                # Calculate position (PDF coordinates start from bottom-left)
                x = coords['x']
                y = page_size[1] - coords['y'] - coords['height']  # Flip Y coordinate
                
                # Handle different field types
                if field['type'] == 'checkbox':
                    if str(value).lower() in ['true', '1', 'yes', 'x']:
                        overlay_canvas.drawString(x, y, 'X')
                elif field['type'] == 'number':
                    try:
                        formatted_value = f"{float(value):,.2f}" if '.' in str(value) else f"{int(value):,}"
                        overlay_canvas.drawString(x, y, formatted_value)
                    except:
                        overlay_canvas.drawString(x, y, str(value))
                else:
                    # Text field
                    text = str(value)
                    
                    # Handle long text by wrapping
                    max_width = coords['width']
                    if len(text) * 6 > max_width:  # Rough character width estimate
                        # Truncate if too long
                        chars_per_line = int(max_width / 6)
                        text = text[:chars_per_line]
                    
                    overlay_canvas.drawString(x, y, text)
        
        overlay_canvas.save()
        packet.seek(0)
        return packet
    
    def fill_pdf_from_csv(self, pdf_path, csv_file, mapping_file, output_path):
        """Fill PDF using coordinate mapping and CSV data"""
        
        # Load field mapping
        if not self.load_field_mapping(mapping_file):
            return False
        
        try:
            # Read CSV data
            csv_data = {}
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                csv_data = next(reader)  # Get first row
            
            print(f"📊 CSV data loaded: {list(csv_data.keys())}")
            
            # Read original PDF
            with open(pdf_path, 'rb') as f:
                existing_pdf = PdfReader(f)
                output_pdf = PdfWriter()
                
                # Get page dimensions
                first_page = existing_pdf.pages[0]
                page_box = first_page.mediabox
                page_width = float(page_box.width)
                page_height = float(page_box.height)
                
                print(f"📄 PDF dimensions: {page_width} x {page_height}")
                
                # Create overlay for each page
                for page_num, page in enumerate(existing_pdf.pages):
                    # Filter fields for this page
                    page_fields = [f for f in self.mappings.get('fields', []) 
                                 if f.get('page', 1) == page_num + 1]
                    
                    if page_fields:
                        # Create overlay with fields for this page
                        page_mapping = {'fields': page_fields}
                        overlay_pdf_buffer = self.create_overlay_pdf(
                            csv_data, page_mapping, (page_width, page_height)
                        )
                        
                        # Read overlay PDF
                        overlay_pdf = PdfReader(overlay_pdf_buffer)
                        overlay_page = overlay_pdf.pages[0]
                        
                        # Merge overlay with original page
                        page.merge_page(overlay_page)
                    
                    output_pdf.add_page(page)
                
                # Save filled PDF
                with open(output_path, 'wb') as output_file:
                    output_pdf.write(output_file)
                
                print(f"✅ Filled PDF saved: {output_path}")
                return True
                
        except Exception as e:
            print(f"❌ Error filling PDF: {e}")
            return False
    
    def fill_multiple_pdfs(self, pdf_directory, csv_file, mapping_file, output_directory):
        """Fill multiple PDFs using same mapping and CSV data"""
        
        if not self.load_field_mapping(mapping_file):
            return
        
        pdf_dir = Path(pdf_directory)
        output_dir = Path(output_directory)
        output_dir.mkdir(exist_ok=True)
        
        # Read all CSV rows
        csv_rows = []
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            csv_rows = list(reader)
        
        print(f"📊 Loaded {len(csv_rows)} CSV records")
        
        # Process each PDF
        pdf_files = list(pdf_dir.glob('*.pdf'))
        
        for pdf_file in pdf_files:
            print(f"\n🔄 Processing: {pdf_file.name}")
            
            # Fill PDF for each CSV row
            for i, csv_row in enumerate(csv_rows):
                client_name = csv_row.get('buyer_name', f'client_{i+1}')
                safe_name = "".join(c for c in client_name if c.isalnum() or c in ' _-').strip()
                
                output_filename = f"{safe_name}_{pdf_file.stem}.pdf"
                output_path = output_dir / output_filename
                
                success = self.fill_pdf_from_csv_single_row(
                    str(pdf_file), csv_row, output_path
                )
                
                if success:
                    print(f"   ✅ Created: {output_filename}")
                else:
                    print(f"   ❌ Failed: {output_filename}")
    
    def fill_pdf_from_csv_single_row(self, pdf_path, csv_row, output_path):
        """Fill PDF with a single CSV row"""
        try:
            # Read original PDF
            with open(pdf_path, 'rb') as f:
                existing_pdf = PdfReader(f)
                output_pdf = PdfWriter()
                
                # Get page dimensions
                first_page = existing_pdf.pages[0]
                page_box = first_page.mediabox
                page_width = float(page_box.width)
                page_height = float(page_box.height)
                
                # Create overlay for each page
                for page_num, page in enumerate(existing_pdf.pages):
                    # Filter fields for this page
                    page_fields = [f for f in self.mappings.get('fields', []) 
                                 if f.get('page', 1) == page_num + 1]
                    
                    if page_fields:
                        # Create overlay with fields for this page
                        page_mapping = {'fields': page_fields}
                        overlay_pdf_buffer = self.create_overlay_pdf(
                            csv_row, page_mapping, (page_width, page_height)
                        )
                        
                        # Read overlay PDF
                        overlay_pdf = PdfReader(overlay_pdf_buffer)
                        overlay_page = overlay_pdf.pages[0]
                        
                        # Merge overlay with original page
                        page.merge_page(overlay_page)
                    
                    output_pdf.add_page(page)
                
                # Save filled PDF
                with open(output_path, 'wb') as output_file:
                    output_pdf.write(output_file)
                
                return True
                
        except Exception as e:
            print(f"❌ Error filling PDF: {e}")
            return False

def main():
    """Demo the coordinate-based PDF filler"""
    filler = CoordinatePDFFiller()
    
    # Check for required files
    if not Path('pdf_field_mapping.json').exists():
        print("❌ No field mapping found!")
        print("📋 Use visual_field_mapper.html to create field mapping first")
        print("   1. Open visual_field_mapper.html in browser")
        print("   2. Load your PDF")
        print("   3. Drag rectangles over fillable areas")
        print("   4. Label each field (buyer_name, purchase_price, etc.)")
        print("   5. Export mapping as pdf_field_mapping.json")
        return
    
    if not Path('sample_clients.csv').exists():
        print("❌ No CSV data found!")
        print("📊 Create sample_clients.csv with your data")
        return
    
    # Demo fill
    test_pdf = 'California_Residential_Purchase_Agreement_-_1224_ts77432.pdf'
    if Path(test_pdf).exists():
        success = filler.fill_pdf_from_csv(
            test_pdf,
            'sample_clients.csv',
            'pdf_field_mapping.json',
            'coordinate_filled_output.pdf'
        )
        
        if success:
            print("\n🎉 SUCCESS! Check coordinate_filled_output.pdf")
        else:
            print("\n❌ FAILED! Check error messages above")
    else:
        print(f"❌ Test PDF not found: {test_pdf}")

if __name__ == "__main__":
    main()