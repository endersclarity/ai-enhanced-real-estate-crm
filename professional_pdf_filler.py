#!/usr/bin/env python3
"""
Professional PDF Form Filler
Creates clean, professional-looking filled forms that match the original exactly
"""

import os
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfform
import io


class ProfessionalPDFFiller:
    """Create professional, clean filled PDFs"""
    
    def __init__(self):
        self.output_dir = "professional_filled_forms"
        self.ensure_output_dir()
        
        # Professional field mappings with precise coordinates
        # These should be calibrated to match your specific form
        self.field_mappings = {
            # Page 1 - Main purchase agreement fields
            'buyer_name': {'x': 150, 'y': 720, 'font_size': 10, 'color': black},
            'property_address': {'x': 150, 'y': 690, 'font_size': 10, 'color': black},
            'property_city': {'x': 150, 'y': 665, 'font_size': 10, 'color': black},
            'purchase_price': {'x': 400, 'y': 500, 'font_size': 12, 'color': black},
            'seller_name': {'x': 150, 'y': 200, 'font_size': 10, 'color': black},
            'date_prepared': {'x': 450, 'y': 750, 'font_size': 9, 'color': black},
        }
    
    def ensure_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def create_fillable_template(self, original_pdf: str, output_name: str = "fillable_template.pdf") -> str:
        """Create a fillable version of the flattened PDF"""
        output_path = os.path.join(self.output_dir, output_name)
        
        try:
            # Read the original PDF
            with open(original_pdf, 'rb') as file:
                reader = PdfReader(file)
                
                # Create new PDF with form fields
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                
                # Add form fields at specified locations
                for field_name, field_info in self.field_mappings.items():
                    # Create text field
                    can.acroForm.textfield(
                        name=field_name,
                        x=field_info['x'],
                        y=field_info['y'],
                        width=200,
                        height=20,
                        textColor=field_info['color'],
                        fontSize=field_info['font_size'],
                        fillColor=None,
                        borderColor=None,
                        forceBorder=False
                    )
                
                can.save()
                
                # Merge form fields with original PDF
                packet.seek(0)
                form_pdf = PdfReader(packet)
                writer = PdfWriter()
                
                # Merge each page
                for i, page in enumerate(reader.pages):
                    if i < len(form_pdf.pages):
                        page.merge_page(form_pdf.pages[i])
                    writer.add_page(page)
                
                # Write the fillable PDF
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                    
                print(f"✅ Created fillable template: {output_path}")
                return output_path
                
        except Exception as e:
            print(f"❌ Error creating fillable template: {e}")
            return None
    
    def fill_pdf_forms(self, template_pdf: str, csv_data: pd.DataFrame) -> list:
        """Fill PDF forms with data from CSV"""
        filled_pdfs = []
        
        for index, row in csv_data.iterrows():
            try:
                buyer_name = str(row.get('buyer_name', f'Buyer_{index+1}')).replace(' ', '_')
                output_path = os.path.join(self.output_dir, f"{buyer_name}_PROFESSIONAL.pdf")
                
                # Read the template
                with open(template_pdf, 'rb') as file:
                    reader = PdfReader(file)
                    writer = PdfWriter()
                    
                    # Copy all pages
                    for page in reader.pages:
                        writer.add_page(page)
                    
                    # Fill form fields
                    field_values = {}
                    for field_name in self.field_mappings.keys():
                        if field_name in row and pd.notna(row[field_name]):
                            value = self._format_value(field_name, row[field_name])
                            field_values[field_name] = value
                    
                    # Update form field values
                    if field_values and len(writer.pages) > 0:
                        writer.update_page_form_field_values(writer.pages[0], field_values)
                    
                    # Write filled PDF
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    
                    filled_pdfs.append(output_path)
                    print(f"✅ Created: {os.path.basename(output_path)}")
                    
            except Exception as e:
                print(f"❌ Error filling form for row {index}: {e}")
                continue
        
        return filled_pdfs
    
    def create_clean_overlay(self, original_pdf: str, csv_data: pd.DataFrame) -> list:
        """Create clean overlays that look professional"""
        filled_pdfs = []
        
        for index, row in csv_data.iterrows():
            try:
                buyer_name = str(row.get('buyer_name', f'Buyer_{index+1}')).replace(' ', '_')
                output_path = os.path.join(self.output_dir, f"{buyer_name}_CLEAN_OVERLAY.pdf")
                
                # Create clean overlay
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                
                # Set professional appearance
                can.setFont("Helvetica", 10)
                
                # Add data at precise locations with proper formatting
                for field_name, field_info in self.field_mappings.items():
                    if field_name in row and pd.notna(row[field_name]):
                        value = self._format_value(field_name, row[field_name])
                        
                        # Set font and color
                        can.setFont("Helvetica", field_info['font_size'])
                        can.setFillColor(field_info['color'])
                        
                        # Draw text cleanly
                        can.drawString(field_info['x'], field_info['y'], value)
                
                can.save()
                
                # Merge with original
                packet.seek(0)
                overlay_pdf = PdfReader(packet)
                
                with open(original_pdf, 'rb') as file:
                    background_pdf = PdfReader(file)
                    writer = PdfWriter()
                    
                    for i, page in enumerate(background_pdf.pages):
                        if i < len(overlay_pdf.pages):
                            page.merge_page(overlay_pdf.pages[i])
                        writer.add_page(page)
                    
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                
                filled_pdfs.append(output_path)
                print(f"✅ Created clean overlay: {os.path.basename(output_path)}")
                
            except Exception as e:
                print(f"❌ Error creating overlay for row {index}: {e}")
                continue
        
        return filled_pdfs
    
    def _format_value(self, field_name: str, value) -> str:
        """Format values appropriately for each field type"""
        if pd.isna(value):
            return ""
        
        value_str = str(value).strip()
        
        if "price" in field_name.lower() or "amount" in field_name.lower():
            try:
                # Clean and format currency
                clean_value = value_str.replace(",", "").replace("$", "")
                num_value = float(clean_value)
                return f"${num_value:,.0f}"
            except:
                return value_str
        elif "date" in field_name.lower():
            try:
                dt = pd.to_datetime(value_str)
                return dt.strftime("%m/%d/%Y")
            except:
                return value_str
        else:
            return value_str
    
    def calibrate_positions(self, pdf_path: str):
        """Helper to calibrate field positions - creates a test PDF with coordinate grid"""
        output_path = os.path.join(self.output_dir, "calibration_grid.pdf")
        
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            width, height = letter
            
            # Draw coordinate grid
            can.setStrokeColor(black)
            can.setFont("Helvetica", 8)
            
            # Vertical lines every 50 points
            for x in range(0, int(width), 50):
                can.line(x, 0, x, height)
                can.drawString(x + 2, height - 20, str(x))
            
            # Horizontal lines every 50 points  
            for y in range(0, int(height), 50):
                can.line(0, y, width, y)
                can.drawString(5, y + 2, str(y))
            
            # Mark current field positions
            can.setFillColor(black)
            for field_name, field_info in self.field_mappings.items():
                x, y = field_info['x'], field_info['y']
                can.circle(x, y, 5, fill=1)
                can.drawString(x + 10, y, field_name)
            
            can.save()
            
            # Merge with original
            packet.seek(0)
            grid_pdf = PdfReader(packet)
            writer = PdfWriter()
            
            for i, page in enumerate(reader.pages):
                if i < len(grid_pdf.pages):
                    page.merge_page(grid_pdf.pages[i])
                writer.add_page(page)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            print(f"📐 Calibration grid created: {output_path}")
            print("Use this to adjust field coordinates in the field_mappings dictionary")


def main():
    """Demo the professional PDF filler"""
    filler = ProfessionalPDFFiller()
    
    try:
        # Load CSV data
        df = pd.read_csv("sample_zipform_data.csv")
        
        # Method 1: Create clean overlays (recommended for flattened PDFs)
        print("🎨 Creating clean overlays...")
        clean_files = filler.create_clean_overlay("template.pdf", df)
        
        # Method 2: Create calibration grid for position adjustment
        print("\n📐 Creating calibration grid...")
        filler.calibrate_positions("template.pdf")
        
        print(f"\n🎉 Created {len(clean_files)} professional PDFs")
        print("📁 Check the 'professional_filled_forms/' directory")
        print("📐 Use 'calibration_grid.pdf' to adjust field positions")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()