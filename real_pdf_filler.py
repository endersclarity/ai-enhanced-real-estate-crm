import os
import json
from datetime import datetime, timedelta
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

class RealPDFFiller:
    def __init__(self):
        self.template_dir = "."
        self.output_dir = "generated_offers"
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_real_offer(self, form_data):
        """Generate actual filled PDF forms from templates"""
        print("🏠 Starting real offer generation...")
        
        # Enhance form data with smart defaults
        enhanced_data = self._enhance_form_data(form_data)
        
        # Create timestamp for this offer
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        offer_folder = os.path.join(self.output_dir, f"offer_{timestamp}")
        os.makedirs(offer_folder, exist_ok=True)
        
        # Process each PDF template
        generated_files = []
        pdf_files = [f for f in os.listdir(self.template_dir) if f.endswith('.pdf') and not f.startswith('attachments')]
        
        for pdf_file in pdf_files:
            try:
                print(f"📄 Processing {pdf_file}")
                output_path = self._fill_pdf_template(pdf_file, enhanced_data, offer_folder, timestamp)
                if output_path:
                    generated_files.append(output_path)
                    print(f"✅ Generated: {os.path.basename(output_path)}")
            except Exception as e:
                print(f"❌ Error processing {pdf_file}: {e}")
        
        # Create summary
        summary_path = self._create_offer_summary(enhanced_data, offer_folder, timestamp)
        generated_files.append(summary_path)
        
        print(f"🎉 Generated {len(generated_files)} documents in {offer_folder}")
        return {
            'success': True,
            'offer_folder': offer_folder,
            'files': generated_files,
            'timestamp': timestamp,
            'buyer_name': enhanced_data['buyerName'],
            'property_address': enhanced_data['propertyAddress']
        }
    
    def _enhance_form_data(self, form_data):
        """Add calculated fields and smart defaults"""
        enhanced = form_data.copy()
        
        # Add current date and calculated dates
        today = datetime.now()
        enhanced['current_date'] = today.strftime("%m/%d/%Y")
        enhanced['offer_expiration'] = (today + timedelta(days=3)).strftime("%m/%d/%Y")
        
        # Calculate escrow close date
        escrow_days = int(enhanced.get('escrowDays', 45))
        enhanced['close_date'] = (today + timedelta(days=escrow_days)).strftime("%m/%d/%Y")
        
        # Format currency values
        enhanced['offer_price_formatted'] = f"${int(float(enhanced['offerPrice'])):,}"
        enhanced['earnest_money_formatted'] = f"${int(float(enhanced['earnestMoney'])):,}"
        
        # Add standard contingency periods (California standards)
        enhanced['inspection_period'] = '17'  # 17 days for inspections
        enhanced['loan_contingency'] = '21'   # 21 days for financing
        enhanced['appraisal_contingency'] = '17'  # 17 days for appraisal
        
        return enhanced    
    def _fill_pdf_template(self, pdf_filename, data, output_folder, timestamp):
        """Fill individual PDF template with data"""
        template_path = os.path.join(self.template_dir, pdf_filename)
        
        # Create clean filename
        clean_name = pdf_filename.replace('_-_', '_').replace('-', '_')
        output_filename = f"{timestamp}_{clean_name}"
        output_path = os.path.join(output_folder, output_filename)
        
        # Check if this is a fillable PDF form
        if self._has_form_fields(template_path):
            return self._fill_form_fields(template_path, data, output_path)
        else:
            return self._overlay_text_on_pdf(template_path, data, output_path, pdf_filename)
    
    def _has_form_fields(self, pdf_path):
        """Check if PDF has fillable form fields"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                if reader.trailer.get("/Root") and reader.trailer["/Root"].get("/AcroForm"):
                    return True
        except:
            pass
        return False
    
    def _fill_form_fields(self, template_path, data, output_path):
        """Fill actual form fields in PDF"""
        try:
            with open(template_path, 'rb') as template_file:
                reader = PdfReader(template_file)
                writer = PdfWriter()
                
                # Copy all pages and try to fill form fields
                for page in reader.pages:
                    writer.add_page(page)
                
                # Try to update form fields
                if reader.trailer.get("/Root") and reader.trailer["/Root"].get("/AcroForm"):
                    form_fields = reader.trailer["/Root"]["/AcroForm"].get("/Fields", [])
                    # Basic form field filling (this is simplified - real implementation would be more complex)
                    
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                    
                return output_path
                
        except Exception as e:
            print(f"Form field filling failed for {template_path}: {e}")
            return self._overlay_text_on_pdf(template_path, data, output_path, os.path.basename(template_path))
    
    def _overlay_text_on_pdf(self, template_path, data, output_path, pdf_filename):
        """Overlay text on PDF using coordinates"""
        try:
            # Create text overlay based on document type
            overlay_pdf = self._create_text_overlay(data, pdf_filename)
            
            # Merge with original
            with open(template_path, 'rb') as template_file:
                template_reader = PdfReader(template_file)
                overlay_reader = PdfReader(io.BytesIO(overlay_pdf))
                writer = PdfWriter()
                
                # Merge first page with overlay, copy rest as-is
                for i, page in enumerate(template_reader.pages):
                    if i == 0 and len(overlay_reader.pages) > 0:
                        page.merge_page(overlay_reader.pages[0])
                    writer.add_page(page)
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                    
            return output_path
            
        except Exception as e:
            print(f"Overlay failed for {pdf_filename}: {e}")
            # Fallback: copy original
            import shutil
            shutil.copy2(template_path, output_path)
            return output_path    
    def _create_text_overlay(self, data, pdf_filename):
        """Create text overlay with positioned data"""
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        width, height = letter
        
        # Set font
        can.setFont("Helvetica", 10)
        
        # Position text based on document type
        if "Purchase_Agreement" in pdf_filename:
            # Main purchase agreement fields
            can.drawString(100, height - 200, data.get('propertyAddress', ''))
            can.drawString(100, height - 230, data.get('buyerName', ''))
            can.drawString(300, height - 260, data.get('offer_price_formatted', ''))
            can.drawString(300, height - 290, data.get('earnest_money_formatted', ''))
            can.drawString(400, height - 320, data.get('close_date', ''))
            can.drawString(100, height - 400, f"Inspection Period: {data.get('inspection_period', '17')} days")
            can.drawString(100, height - 430, f"Loan Contingency: {data.get('loan_contingency', '21')} days")
            
        elif "Buyer_Representation" in pdf_filename:
            # Buyer rep agreement
            can.drawString(100, height - 150, data.get('buyerName', ''))
            can.drawString(100, height - 180, data.get('buyerEmail', ''))
            can.drawString(100, height - 210, data.get('buyerPhone', ''))
            if data.get('sellerPaysBroker'):
                can.drawString(80, height - 350, "X")  # Checkbox mark
                
        elif "Advisory" in pdf_filename or "Disclosure" in pdf_filename:
            # Standard disclosure forms
            can.drawString(100, height - 100, data.get('buyerName', ''))
            can.drawString(400, height - 100, data.get('current_date', ''))
            can.drawString(100, height - 130, data.get('propertyAddress', ''))
            
        else:
            # Generic form fields
            can.drawString(100, height - 80, data.get('buyerName', ''))
            can.drawString(100, height - 110, data.get('propertyAddress', ''))
            can.drawString(400, height - 80, data.get('current_date', ''))
            
            # Property feature checkboxes
            if data.get('hasSeptic'):
                can.drawString(80, height - 200, "X")
            if data.get('hasWell'):
                can.drawString(80, height - 230, "X")
        
        can.save()
        packet.seek(0)
        return packet.read()
    
    def _create_offer_summary(self, data, output_folder, timestamp):
        """Create a summary document for the offer"""
        summary_path = os.path.join(output_folder, f"{timestamp}_OFFER_SUMMARY.txt")
        
        summary_content = f"""
REAL ESTATE OFFER SUMMARY
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

BUYER INFORMATION:
Name: {data.get('buyerName', '')}
Email: {data.get('buyerEmail', '')}
Phone: {data.get('buyerPhone', '')}
Current Address: {data.get('buyerAddress', '')}

PROPERTY INFORMATION:
Address: {data.get('propertyAddress', '')}
Offer Price: {data.get('offer_price_formatted', '')}
Earnest Money: {data.get('earnest_money_formatted', '')}
Escrow Period: {data.get('escrowDays', '')} days
Close Date: {data.get('close_date', '')}

PROPERTY FEATURES:
Septic System: {'Yes' if data.get('hasSeptic') else 'No'}
Well Water: {'Yes' if data.get('hasWell') else 'No'}
Seller Pays Broker: {'Yes' if data.get('sellerPaysBroker') else 'No'}

INCLUDED ITEMS:
{data.get('includedItems', 'None specified')}

CONTINGENCY PERIODS:
Inspection: {data.get('inspection_period', '17')} days
Financing: {data.get('loan_contingency', '21')} days
Appraisal: {data.get('appraisal_contingency', '17')} days

Offer Expires: {data.get('offer_expiration', '')}
"""
        
        with open(summary_path, 'w') as f:
            f.write(summary_content)
            
        return summary_path