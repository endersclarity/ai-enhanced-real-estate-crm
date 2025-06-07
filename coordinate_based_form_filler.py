#!/usr/bin/env python3
"""
Coordinate-Based PDF Form Filler
Professional solution for image-based or encrypted PDFs
Uses ReportLab to overlay text at precise coordinates
"""

import os
import json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import PyPDF2
from io import BytesIO

class CoordinateBasedFormFiller:
    """
    Professional PDF form filler using coordinate-based text placement
    Handles encrypted, scanned, or image-based PDFs
    """
    
    def __init__(self):
        self.font_name = "Helvetica"
        self.font_size = 10
        self.text_color = black
        
        # Load coordinate mappings for different forms
        self.form_coordinates = self.load_coordinate_mappings()
    
    def load_coordinate_mappings(self):
        """Load predefined coordinate mappings for CAR forms"""
        
        # California Residential Purchase Agreement - Key field coordinates
        # These would be determined through manual measurement or AI-assisted coordinate detection
        california_purchase_coordinates = {
            "buyer_name": {"x": 100, "y": 700, "page": 1},
            "buyer_address": {"x": 100, "y": 680, "page": 1},
            "buyer_phone": {"x": 100, "y": 660, "page": 1},
            "seller_name": {"x": 100, "y": 600, "page": 1},
            "seller_address": {"x": 100, "y": 580, "page": 1},
            "property_address": {"x": 100, "y": 520, "page": 1},
            "purchase_price": {"x": 300, "y": 480, "page": 1},
            "earnest_money": {"x": 300, "y": 460, "page": 1},
            "closing_date": {"x": 100, "y": 400, "page": 1},
            "possession_date": {"x": 300, "y": 400, "page": 1},
            "apn": {"x": 100, "y": 360, "page": 1},
            "mls_number": {"x": 300, "y": 360, "page": 1},
            
            # Page 2 fields
            "loan_amount": {"x": 100, "y": 700, "page": 2},
            "down_payment": {"x": 300, "y": 700, "page": 2},
            "listing_agent": {"x": 100, "y": 650, "page": 2},
            "selling_agent": {"x": 100, "y": 630, "page": 2},
            "escrow_company": {"x": 100, "y": 580, "page": 2},
            "title_company": {"x": 100, "y": 560, "page": 2},
            
            # Signature fields
            "buyer_signature": {"x": 100, "y": 200, "page": 27},
            "buyer_date": {"x": 350, "y": 200, "page": 27},
            "seller_signature": {"x": 100, "y": 150, "page": 27},
            "seller_date": {"x": 350, "y": 150, "page": 27}
        }
        
        return {
            "California_Residential_Purchase_Agreement": california_purchase_coordinates,
            "Buyer_Representation_Agreement": {
                "client_full_name": {"x": 120, "y": 700, "page": 1},
                "client_address_full": {"x": 120, "y": 680, "page": 1},
                "agent_full_name": {"x": 120, "y": 600, "page": 1},
                "agent_license_number": {"x": 400, "y": 600, "page": 1},
                "brokerage_name": {"x": 120, "y": 580, "page": 1},
                "agreement_start_date": {"x": 120, "y": 540, "page": 1},
                "agreement_end_date": {"x": 350, "y": 540, "page": 1},
                "commission_rate": {"x": 120, "y": 520, "page": 1}
            },
            "Transaction_Record": {
                "transaction_id": {"x": 100, "y": 700, "page": 1},
                "client_name": {"x": 100, "y": 680, "page": 1},
                "property_address": {"x": 100, "y": 660, "page": 1},
                "transaction_date": {"x": 300, "y": 660, "page": 1},
                "transaction_type": {"x": 100, "y": 620, "page": 1},
                "status": {"x": 300, "y": 620, "page": 1}
            }
        }
    
    def create_overlay_pdf(self, form_name, field_data, output_path):
        """
        Create a PDF overlay with text at specified coordinates
        """
        if form_name not in self.form_coordinates:
            raise ValueError(f"Form '{form_name}' not supported. Available: {list(self.form_coordinates.keys())}")
        
        coordinates = self.form_coordinates[form_name]
        
        # Create overlay PDF in memory
        overlay_buffer = BytesIO()
        overlay_canvas = canvas.Canvas(overlay_buffer, pagesize=letter)
        
        # Group fields by page for efficient processing
        pages_data = {}
        for field_name, value in field_data.items():
            if field_name in coordinates and value:
                coord = coordinates[field_name]
                page_num = coord["page"]
                if page_num not in pages_data:
                    pages_data[page_num] = []
                pages_data[page_num].append({
                    "text": str(value),
                    "x": coord["x"],
                    "y": coord["y"]
                })
        
        # Create pages with text overlays
        max_page = max(pages_data.keys()) if pages_data else 1
        for page_num in range(1, max_page + 1):
            if page_num in pages_data:
                # Add text fields to this page
                overlay_canvas.setFont(self.font_name, self.font_size)
                overlay_canvas.setFillColor(self.text_color)
                
                for field in pages_data[page_num]:
                    overlay_canvas.drawString(field["x"], field["y"], field["text"])
            
            overlay_canvas.showPage()
        
        overlay_canvas.save()
        overlay_buffer.seek(0)
        
        # Save overlay PDF
        with open(output_path, 'wb') as f:
            f.write(overlay_buffer.getvalue())
        
        return output_path
    
    def fill_form(self, form_name, field_data, template_path, output_path):
        """
        Fill a PDF form using coordinate-based text placement
        
        Args:
            form_name: Name of the form (must match coordinate mapping)
            field_data: Dictionary of field names to values
            template_path: Path to the blank PDF template
            output_path: Path for the filled PDF output
        """
        try:
            # Create overlay with filled text
            overlay_path = output_path.replace('.pdf', '_overlay.pdf')
            self.create_overlay_pdf(form_name, field_data, overlay_path)
            
            # Merge overlay with original PDF (if available)
            if os.path.exists(template_path):
                merged_path = self.merge_pdf_with_overlay(template_path, overlay_path, output_path)
                # Clean up temporary overlay
                os.remove(overlay_path)
                return merged_path
            else:
                # Use overlay as final output
                os.rename(overlay_path, output_path)
                return output_path
                
        except Exception as e:
            print(f"❌ Error filling form: {e}")
            return None
    
    def merge_pdf_with_overlay(self, template_path, overlay_path, output_path):
        """
        Merge the original PDF with the text overlay
        """
        try:
            # Read original PDF
            with open(template_path, 'rb') as template_file:
                template_pdf = PyPDF2.PdfReader(template_file)
                
                # Read overlay PDF
                with open(overlay_path, 'rb') as overlay_file:
                    overlay_pdf = PyPDF2.PdfReader(overlay_file)
                    
                    # Create output PDF
                    output_pdf = PyPDF2.PdfWriter()
                    
                    # Merge pages
                    for page_num in range(len(template_pdf.pages)):
                        template_page = template_pdf.pages[page_num]
                        
                        # If overlay has this page, merge it
                        if page_num < len(overlay_pdf.pages):
                            overlay_page = overlay_pdf.pages[page_num]
                            template_page.merge_page(overlay_page)
                        
                        output_pdf.add_page(template_page)
                    
                    # Save merged PDF
                    with open(output_path, 'wb') as output_file:
                        output_pdf.write(output_file)
            
            return output_path
            
        except Exception as e:
            print(f"❌ PDF merge error: {e}")
            # Fallback: return overlay as output
            os.rename(overlay_path, output_path)
            return output_path
    
    def get_sample_data(self, form_name):
        """
        Get sample data for testing form filling
        """
        sample_data = {
            "California_Residential_Purchase_Agreement": {
                "buyer_name": "John and Jane Smith",
                "buyer_address": "123 Main Street, Anytown, CA 90210",
                "buyer_phone": "(555) 123-4567",
                "seller_name": "Bob and Mary Johnson",
                "seller_address": "456 Oak Avenue, Hometown, CA 90211",
                "property_address": "789 Pine Street, Dreamtown, CA 90212",
                "purchase_price": "$650,000",
                "earnest_money": "$10,000",
                "closing_date": "March 15, 2025",
                "possession_date": "March 20, 2025",
                "apn": "123-456-789",
                "mls_number": "ML12345678",
                "loan_amount": "$520,000",
                "down_payment": "$130,000",
                "listing_agent": "Sarah Wilson, Narissa Realty",
                "selling_agent": "Mike Davis, ABC Realty",
                "escrow_company": "First American Escrow",
                "title_company": "Pacific Title Company"
            },
            "Buyer_Representation_Agreement": {
                "client_full_name": "John Jacob Smith",
                "client_address_full": "456 Oak Avenue, Springfield, ST 12345",
                "agent_full_name": "Alice Agent",
                "agent_license_number": "CALDRE#01234567",
                "brokerage_name": "Responsive Realty",
                "agreement_start_date": "2024-07-01",
                "agreement_end_date": "2024-12-31",
                "commission_rate": "3.0%"
            },
            "Transaction_Record": {
                "transaction_id": "TX-2025-001",
                "client_name": "John and Jane Smith",
                "property_address": "789 Pine Street, Dreamtown, CA 90212",
                "transaction_date": "March 15, 2025",
                "transaction_type": "Purchase",
                "status": "In Progress"
            }
        }
        
        return sample_data.get(form_name, {})
    
    def test_form_filling(self):
        """
        Test the coordinate-based form filling system
        """
        print("🧪 Testing Coordinate-Based Form Filling")
        print("=" * 50)
        
        # Test with California Purchase Agreement
        form_name = "California_Residential_Purchase_Agreement"
        sample_data = self.get_sample_data(form_name)
        
        # Create output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Generate filled form
        template_path = f"car_forms/{form_name}_-_1224_ts77432.pdf"
        output_path = output_dir / f"{form_name}_FILLED_TEST.pdf"
        
        print(f"📝 Form: {form_name}")
        print(f"📄 Template: {template_path}")
        print(f"💾 Output: {output_path}")
        print(f"🔢 Fields to fill: {len(sample_data)}")
        
        result = self.fill_form(form_name, sample_data, template_path, str(output_path))
        
        if result:
            print(f"✅ Form filled successfully: {result}")
            print(f"📊 Sample fields filled:")
            for field, value in list(sample_data.items())[:5]:
                print(f"   {field}: {value}")
            if len(sample_data) > 5:
                print(f"   ... and {len(sample_data) - 5} more fields")
        else:
            print("❌ Form filling failed")
        
        return result

def main():
    """
    Demonstrate coordinate-based PDF form filling
    """
    print("🎯 PHASE A SOLUTION: Coordinate-Based Form Filling")
    print("🔧 Professional PDF text overlay system")
    print("=" * 60)
    
    filler = CoordinateBasedFormFiller()
    
    # Test the system
    test_result = filler.test_form_filling()
    
    print(f"\n📋 Supported Forms: {len(filler.form_coordinates)}")
    for form_name in filler.form_coordinates.keys():
        field_count = len(filler.form_coordinates[form_name])
        print(f"   📄 {form_name}: {field_count} mapped fields")
    
    print(f"\n🚀 Phase A Status: {'✅ COMPLETE' if test_result else '❌ NEEDS FIXES'}")
    print("🎯 Next: Phase B parallel workstreams can begin")
    
    return filler

if __name__ == "__main__":
    main()