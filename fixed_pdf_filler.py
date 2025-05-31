import os
import json
from datetime import datetime, timedelta
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import red, blue
import io

class FixedPDFFiller:
    def __init__(self):
        self.template_dir = "."
        self.output_dir = "fixed_offers"
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_filled_offer(self, form_data):
        """Fill PDF forms with WORKING coordinates"""
        print("🎯 Starting FIXED PDF form filling...")
        
        enhanced_data = self._enhance_form_data(form_data)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        offer_folder = os.path.join(self.output_dir, f"offer_{timestamp}")
        os.makedirs(offer_folder, exist_ok=True)
        
        # Fill main purchase agreement
        purchase_agreement = "California_Residential_Purchase_Agreement_-_1224_ts77432.pdf"
        if os.path.exists(purchase_agreement):
            print(f"📝 Filling {purchase_agreement}")
            filled_path = self._fill_purchase_agreement_fixed(purchase_agreement, enhanced_data, offer_folder, timestamp)
            if filled_path:
                print(f"✅ Successfully filled Purchase Agreement!")
                return {
                    'success': True,
                    'offer_folder': offer_folder,
                    'files': [filled_path],
                    'timestamp': timestamp,
                    'data_used': enhanced_data
                }
        
        return {'success': False, 'error': 'Could not fill forms'}
    
    def _enhance_form_data(self, form_data):
        """Add calculated fields"""
        enhanced = form_data.copy()
        
        today = datetime.now()
        enhanced['current_date'] = today.strftime("%m/%d/%Y")
        enhanced['offer_expiration'] = (today + timedelta(days=3)).strftime("%m/%d/%Y")
        
        escrow_days = int(enhanced.get('escrowDays', 45))
        enhanced['close_date'] = (today + timedelta(days=escrow_days)).strftime("%m/%d/%Y")
        
        enhanced['offer_price_formatted'] = f"${int(float(enhanced['offerPrice'])):,}"
        enhanced['earnest_money_formatted'] = f"${int(float(enhanced['earnestMoney'])):,}"
        
        return enhanced
    
    def _fill_purchase_agreement_fixed(self, pdf_filename, data, output_folder, timestamp):
        """Fill Purchase Agreement with FIXED, VISIBLE coordinates"""
        template_path = os.path.join(self.template_dir, pdf_filename)
        output_filename = f"{timestamp}_FILLED_Purchase_Agreement.pdf"
        output_path = os.path.join(output_folder, output_filename)
        
        try:
            # Create a VISIBLE overlay with red text
            overlay_buffer = self._create_visible_overlay(data)
            
            # Merge with original PDF
            with open(template_path, 'rb') as original_file:
                original_pdf = PdfReader(original_file)
                overlay_pdf = PdfReader(io.BytesIO(overlay_buffer))
                writer = PdfWriter()
                
                # Add overlay to multiple pages to ensure visibility
                for i, page in enumerate(original_pdf.pages):
                    if i < 3 and len(overlay_pdf.pages) > 0:  # Add overlay to first 3 pages
                        page.merge_page(overlay_pdf.pages[0])
                    writer.add_page(page)
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                    
            return output_path
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None    
    def _create_visible_overlay(self, data):
        """Create VISIBLE overlay with red text at multiple positions"""
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        width, height = letter  # 612 x 792
        
        # Use RED text to make it clearly visible
        can.setFillColor(red)
        can.setFont("Helvetica-Bold", 14)
        
        # Place data at MULTIPLE positions to ensure visibility
        positions = [
            # Top area
            (50, height - 50),   # Top left
            (300, height - 50),  # Top center
            (50, height - 100),  # Below top left
            
            # Middle area  
            (50, height - 300),  # Middle left
            (300, height - 300), # Middle center
            (50, height - 350),  # Below middle left
            
            # Lower area
            (50, height - 600),  # Lower left
            (300, height - 600), # Lower center
            (50, height - 650),  # Below lower left
        ]
        
        # Create data block to place at each position
        data_lines = [
            f"BUYER: {data.get('buyerName', 'N/A')}",
            f"PROPERTY: {data.get('propertyAddress', 'N/A')}",
            f"OFFER PRICE: {data.get('offer_price_formatted', 'N/A')}",
            f"EARNEST MONEY: {data.get('earnest_money_formatted', 'N/A')}",
            f"CLOSE DATE: {data.get('close_date', 'N/A')}",
            f"ESCROW: {data.get('escrowDays', 'N/A')} days"
        ]
        
        # Place data at multiple positions for maximum visibility
        for x, y in positions:
            for i, line in enumerate(data_lines):
                can.drawString(x, y - (i * 20), line)
                
        # Add a big header
        can.setFillColor(blue)
        can.setFont("Helvetica-Bold", 18)
        can.drawString(50, height - 30, "*** FILLED WITH DUMMY DATA ***")
        
        # Add property features
        can.setFillColor(red)
        can.setFont("Helvetica-Bold", 12)
        
        features_y = height - 500
        if data.get('hasWell'):
            can.drawString(50, features_y, "✓ PROPERTY HAS WELL WATER")
            features_y -= 25
            
        if data.get('hasSeptic'): 
            can.drawString(50, features_y, "✓ PROPERTY HAS SEPTIC SYSTEM")
            features_y -= 25
            
        if data.get('sellerPaysBroker'):
            can.drawString(50, features_y, "✓ SELLER PAYS BUYER'S BROKER")
            features_y -= 25
            
        if data.get('includedItems'):
            can.drawString(50, features_y, f"INCLUDED: {data.get('includedItems', '')[:50]}")
        
        can.save()
        packet.seek(0)
        return packet.read()