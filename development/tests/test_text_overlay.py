#!/usr/bin/env python3
"""
Test script to overlay text on PDF using reportlab
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os

def create_text_overlay(data):
    """Create a transparent PDF with text overlays"""
    packet = io.BytesIO()
    
    # Create a new PDF with reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 10)
    
    # Add text at specific coordinates (x, y from bottom-left)
    # These coordinates are guesses - we'd need to map them properly
    can.drawString(100, 750, f"Buyer: {data.get('buyer_name', '')}")
    can.drawString(100, 730, f"Seller: {data.get('seller_name', '')}")
    can.drawString(100, 710, f"Property: {data.get('property_address', '')}")
    can.drawString(100, 690, f"Price: {data.get('purchase_price', '')}")
    can.drawString(100, 670, f"Deposit: {data.get('deposit_amount', '')}")
    can.drawString(100, 650, f"Closing Date: {data.get('closing_date', '')}")
    can.drawString(100, 630, f"Agent: {data.get('agent_name', '')}")
    
    can.save()
    
    # Move to the beginning of the StringIO buffer
    packet.seek(0)
    return packet

def overlay_text_on_pdf(template_pdf, output_pdf, data):
    """Overlay text on existing PDF"""
    try:
        # Create the overlay
        overlay_packet = create_text_overlay(data)
        overlay_pdf = PdfReader(overlay_packet)
        
        # Read the template PDF
        template = PdfReader(template_pdf)
        output = PdfWriter()
        
        # Get the first page and overlay text
        page = template.pages[0]
        page.merge_page(overlay_pdf.pages[0])
        output.add_page(page)
        
        # Add remaining pages without overlay
        for i in range(1, len(template.pages)):
            output.add_page(template.pages[i])
        
        # Write the result
        with open(output_pdf, 'wb') as output_file:
            output.write(output_file)
            
        print(f"✅ Successfully created PDF with text overlay: {output_pdf}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating overlay: {e}")
        return False

def main():
    template_file = "California_RPA_Template_Fillable.pdf"
    output_file = "California_RPA_TEXT_OVERLAY_TEST.pdf"
    
    # Real estate data to overlay
    test_data = {
        'buyer_name': 'John Doe',
        'seller_name': 'Jane Smith',
        'property_address': '789 Elm Street, Santa Monica, CA 90401',
        'purchase_price': '$750,000',
        'deposit_amount': '$25,000',
        'closing_date': '2025-07-15',
        'agent_name': 'Narissa Realty Agent'
    }
    
    if not os.path.exists(template_file):
        print(f"Template file not found: {template_file}")
        return
        
    print("🏠 TESTING TEXT OVERLAY APPROACH")
    print("=" * 50)
    
    if overlay_text_on_pdf(template_file, output_file, test_data):
        print(f"\n🎯 TEXT OVERLAY TEST COMPLETE!")
        print(f"   Template: {template_file}")
        print(f"   Output:   {output_file}")
        print(f"   Data overlaid at fixed coordinates")
        print(f"\n📋 Overlaid data:")
        for key, value in test_data.items():
            print(f"  {key}: {value}")
    else:
        print(f"\n❌ Text overlay failed")

if __name__ == "__main__":
    main()