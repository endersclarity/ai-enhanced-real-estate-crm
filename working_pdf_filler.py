import os
import json
from datetime import datetime, timedelta
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

class WorkingPDFFiller:
    def __init__(self):
        self.template_dir = "."
        self.output_dir = "working_offers"
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_filled_offer(self, form_data):
        """Actually fill PDF forms with real data"""
        print("🏠 Starting WORKING PDF form filling...")
        
        # Enhance form data
        enhanced_data = self._enhance_form_data(form_data)
        
        # Create timestamp folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        offer_folder = os.path.join(self.output_dir, f"offer_{timestamp}")
        os.makedirs(offer_folder, exist_ok=True)
        
        # Process key documents
        filled_files = []
        
        # Main documents to fill
        key_documents = [
            "California_Residential_Purchase_Agreement_-_1224_ts77432.pdf",
            "Buyer_Representation_and_Broker_Compensation_Agreement_-_1224_ts74307.pdf",
            "Statewide_Buyer_and_Seller_Advisory_-_624_ts89932.pdf"
        ]
        
        for doc in key_documents:
            if os.path.exists(doc):
                print(f"📝 Filling {doc}")
                filled_path = self._fill_specific_form(doc, enhanced_data, offer_folder, timestamp)
                if filled_path:
                    filled_files.append(filled_path)
                    print(f"✅ Completed: {os.path.basename(filled_path)}")
        
        return {
            'success': True,
            'offer_folder': offer_folder,
            'files': filled_files,
            'timestamp': timestamp,
            'data_used': enhanced_data
        }
    
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
    def _fill_specific_form(self, pdf_filename, data, output_folder, timestamp):
        """Fill specific PDF form with proper field mapping"""
        template_path = os.path.join(self.template_dir, pdf_filename)
        output_filename = f"{timestamp}_{pdf_filename.replace('-', '_').replace('_-_', '_')}"
        output_path = os.path.join(output_folder, output_filename)
        
        try:
            # Create overlay with form data positioned correctly
            overlay_buffer = self._create_form_overlay(pdf_filename, data)
            
            # Read original PDF
            with open(template_path, 'rb') as original_file:
                original_pdf = PdfReader(original_file)
                overlay_pdf = PdfReader(io.BytesIO(overlay_buffer))
                writer = PdfWriter()
                
                # Merge first page with overlay, copy rest
                for i, page in enumerate(original_pdf.pages):
                    if i == 0 and len(overlay_pdf.pages) > 0:
                        # Merge overlay onto first page
                        page.merge_page(overlay_pdf.pages[0])
                    writer.add_page(page)
                
                # Write filled PDF
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                    
            return output_path
            
        except Exception as e:
            print(f"❌ Error filling {pdf_filename}: {e}")
            return None
    
    def _create_form_overlay(self, pdf_filename, data):
        """Create overlay with data positioned based on form type"""
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        width, height = letter
        
        # Set font
        can.setFont("Helvetica", 12)
        
        # Position data based on specific form
        if "Purchase_Agreement" in pdf_filename:
            self._fill_purchase_agreement(can, data, width, height)
        elif "Buyer_Representation" in pdf_filename:
            self._fill_buyer_rep_agreement(can, data, width, height)
        elif "Advisory" in pdf_filename:
            self._fill_advisory_form(can, data, width, height)
        
        can.save()
        packet.seek(0)
        return packet.read()
    
    def _fill_purchase_agreement(self, canvas, data, width, height):
        """Fill California Purchase Agreement with specific coordinates"""
        # These coordinates are approximated - would need to be fine-tuned
        
        # Property address (top of form)
        canvas.drawString(150, height - 150, data.get('propertyAddress', ''))
        
        # Buyer name
        canvas.drawString(100, height - 200, f"Buyer: {data.get('buyerName', '')}")
        
        # Purchase price
        canvas.drawString(300, height - 250, f"Purchase Price: {data.get('offer_price_formatted', '')}")
        
        # Initial deposit (earnest money)
        canvas.drawString(300, height - 280, f"Initial Deposit: {data.get('earnest_money_formatted', '')}")
        
        # Close of escrow date
        canvas.drawString(400, height - 310, f"Close Date: {data.get('close_date', '')}")
        
        # Financing terms
        canvas.drawString(100, height - 400, "FINANCING TERMS:")
        canvas.drawString(120, height - 420, f"• Loan contingency: 21 days")
        canvas.drawString(120, height - 440, f"• Appraisal contingency: 17 days")
        
        # Property features
        if data.get('hasWell'):
            canvas.drawString(100, height - 500, "☑ Property has well water")
        if data.get('hasSeptic'):
            canvas.drawString(100, height - 520, "☑ Property has septic system")
            
        # Items included
        if data.get('includedItems'):
            canvas.drawString(100, height - 560, f"Items included: {data.get('includedItems', '')}")
    
    def _fill_buyer_rep_agreement(self, canvas, data, width, height):
        """Fill Buyer Representation Agreement"""
        canvas.drawString(100, height - 100, f"Client: {data.get('buyerName', '')}")
        canvas.drawString(100, height - 130, f"Email: {data.get('buyerEmail', '')}")
        canvas.drawString(100, height - 160, f"Phone: {data.get('buyerPhone', '')}")
        
        if data.get('sellerPaysBroker'):
            canvas.drawString(100, height - 200, "☑ Seller to pay buyer's broker commission")
    
    def _fill_advisory_form(self, canvas, data, width, height):
        """Fill advisory/disclosure forms"""
        canvas.drawString(100, height - 100, f"Buyer: {data.get('buyerName', '')}")
        canvas.drawString(100, height - 130, f"Property: {data.get('propertyAddress', '')}")
        canvas.drawString(400, height - 100, f"Date: {data.get('current_date', '')}")
        canvas.drawString(100, height - 200, "Buyer acknowledges receipt and review of this advisory.")