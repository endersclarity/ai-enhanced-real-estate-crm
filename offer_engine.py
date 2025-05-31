import os
import json
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
import pdfplumber

class OfferEngine:
    def __init__(self):
        self.forms_dir = "."
        self.output_dir = "output"
        self.template_data = {}
        
    def generate_offer_package(self, form_data):
        """Generate complete offer package from minimal input data"""
        
        # Enhance form data with smart defaults
        enhanced_data = self._enhance_form_data(form_data)
        
        # Process all PDF forms
        processed_files = []
        
        # Core documents that require field mapping
        core_documents = [
            "California_Residential_Purchase_Agreement_-_1224_ts77432.pdf",
            "Buyer_Representation_and_Broker_Compensation_Agreement_-_1224_ts74307.pdf",
            "Statewide_Buyer_and_Seller_Advisory_-_624_ts89932.pdf"
        ]
        
        # Process each document
        for pdf_file in os.listdir(self.forms_dir):
            if pdf_file.endswith('.pdf') and not pdf_file.startswith('attachments'):
                try:
                    output_path = self._process_pdf_form(pdf_file, enhanced_data)
                    if output_path:
                        processed_files.append(output_path)
                except Exception as e:
                    print(f"Error processing {pdf_file}: {e}")
                    
        # Create combined package
        package_path = self._create_package(processed_files, enhanced_data)
        
        return {
            'success': True,
            'package_path': package_path,
            'individual_files': processed_files,
            'message': f'Generated {len(processed_files)} documents'
        }
    
    def _enhance_form_data(self, form_data):
        """Add smart defaults and calculated fields"""
        enhanced = form_data.copy()
        
        # Add current date and calculated dates
        today = datetime.now()
        enhanced['current_date'] = today.strftime('%m/%d/%Y')
        enhanced['offer_expiration'] = (today + timedelta(days=3)).strftime('%m/%d/%Y')
        
        # Calculate escrow close date
        escrow_days = int(enhanced.get('escrowDays', 45))
        enhanced['close_date'] = (today + timedelta(days=escrow_days)).strftime('%m/%d/%Y')
        
        # Format currency values
        enhanced['offer_price_formatted'] = f"${int(enhanced['offerPrice']):,}"
        enhanced['earnest_money_formatted'] = f"${int(enhanced['earnestMoney']):,}"
        
        # Add standard contingency periods
        enhanced['inspection_period'] = '17'  # Standard 17 days
        enhanced['loan_contingency'] = '21'   # Standard 21 days
        enhanced['appraisal_contingency'] = '17'  # Standard 17 days
        
        return enhanced    
    def _process_pdf_form(self, pdf_filename, form_data):
        """Process individual PDF form with data mapping"""
        input_path = os.path.join(self.forms_dir, pdf_filename)
        output_filename = f"filled_{pdf_filename}"
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # Create overlay with form data
            overlay_path = self._create_overlay(pdf_filename, form_data)
            
            # Merge overlay with original PDF
            self._merge_pdfs(input_path, overlay_path, output_path)
            
            # Clean up temporary overlay
            if os.path.exists(overlay_path):
                os.remove(overlay_path)
                
            return output_path
            
        except Exception as e:
            print(f"Error processing {pdf_filename}: {e}")
            return None
    
    def _create_overlay(self, pdf_filename, form_data):
        """Create overlay PDF with form data positioned correctly"""
        overlay_path = f"temp_overlay_{pdf_filename}"
        
        # Get PDF dimensions
        with open(os.path.join(self.forms_dir, pdf_filename), 'rb') as file:
            pdf_reader = PdfReader(file)
            page = pdf_reader.pages[0]
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
        
        # Create overlay
        c = canvas.Canvas(overlay_path, pagesize=(width, height))
        
        # Map data to PDF positions based on document type
        if "Purchase_Agreement" in pdf_filename:
            self._map_purchase_agreement_fields(c, form_data, width, height)
        elif "Buyer_Representation" in pdf_filename:
            self._map_buyer_rep_fields(c, form_data, width, height)
        elif "Advisory" in pdf_filename:
            self._map_advisory_fields(c, form_data, width, height)
        else:
            self._map_standard_fields(c, form_data, width, height)
        
        c.save()
        return overlay_path    
    def _map_purchase_agreement_fields(self, canvas, data, width, height):
        """Map form data to Purchase Agreement PDF positions"""
        canvas.setFont("Helvetica", 10)
        
        # Property address
        canvas.drawString(100, height - 150, data.get('propertyAddress', ''))
        
        # Buyer name
        canvas.drawString(100, height - 200, data.get('buyerName', ''))
        
        # Offer price
        canvas.drawString(200, height - 250, data.get('offer_price_formatted', ''))
        
        # Earnest money
        canvas.drawString(200, height - 280, data.get('earnest_money_formatted', ''))
        
        # Close date
        canvas.drawString(200, height - 310, data.get('close_date', ''))
        
        # Contingency periods
        canvas.drawString(150, height - 400, data.get('inspection_period', '17'))
        canvas.drawString(150, height - 430, data.get('loan_contingency', '21'))
        
    def _map_buyer_rep_fields(self, canvas, data, width, height):
        """Map form data to Buyer Representation Agreement"""
        canvas.setFont("Helvetica", 10)
        
        # Buyer contact info
        canvas.drawString(100, height - 100, data.get('buyerName', ''))
        canvas.drawString(100, height - 130, data.get('buyerEmail', ''))
        canvas.drawString(100, height - 160, data.get('buyerPhone', ''))
        
        # Broker compensation checkbox
        if data.get('sellerPaysBroker', False):
            canvas.drawString(80, height - 300, "X")
    
    def _map_advisory_fields(self, canvas, data, width, height):
        """Map standard fields to advisory documents"""
        canvas.setFont("Helvetica", 10)
        
        # Standard buyer acknowledgment
        canvas.drawString(100, height - 100, data.get('buyerName', ''))
        canvas.drawString(300, height - 100, data.get('current_date', ''))
        
    def _map_standard_fields(self, canvas, data, width, height):
        """Map standard fields to other documents"""
        canvas.setFont("Helvetica", 9)
        
        # Common fields that appear on most forms
        canvas.drawString(100, height - 50, data.get('buyerName', ''))
        canvas.drawString(100, height - 80, data.get('propertyAddress', ''))
        canvas.drawString(400, height - 50, data.get('current_date', ''))
        
        # Property features checkboxes
        if data.get('hasSeptic', False):
            canvas.drawString(80, height - 200, "X")
        if data.get('hasWell', False):
            canvas.drawString(80, height - 230, "X")        
    def _merge_pdfs(self, original_path, overlay_path, output_path):
        """Merge original PDF with overlay"""
        try:
            # Read original PDF
            with open(original_path, 'rb') as original_file:
                original_pdf = PdfReader(original_file)
                
                # Read overlay PDF
                with open(overlay_path, 'rb') as overlay_file:
                    overlay_pdf = PdfReader(overlay_file)
                    
                    # Create writer
                    writer = PdfWriter()
                    
                    # Merge pages
                    for page_num in range(len(original_pdf.pages)):
                        original_page = original_pdf.pages[page_num]
                        
                        # Add overlay to first page only
                        if page_num == 0 and len(overlay_pdf.pages) > 0:
                            overlay_page = overlay_pdf.pages[0]
                            original_page.merge_page(overlay_page)
                        
                        writer.add_page(original_page)
                    
                    # Write output
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                        
        except Exception as e:
            print(f"Error merging PDFs: {e}")
            # Fallback: copy original file
            import shutil
            shutil.copy2(original_path, output_path)
    
    def _create_package(self, file_paths, form_data):
        """Create combined PDF package"""
        package_path = os.path.join(self.output_dir, "complete-offer-package.pdf")
        
        try:
            writer = PdfWriter()
            
            # Add all processed files to package
            for file_path in file_paths:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as file:
                        pdf = PdfReader(file)
                        for page in pdf.pages:
                            writer.add_page(page)
            
            # Write combined package
            with open(package_path, 'wb') as output:
                writer.write(output)
                
            return package_path
            
        except Exception as e:
            print(f"Error creating package: {e}")
            return None