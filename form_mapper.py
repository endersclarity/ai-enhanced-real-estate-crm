import os
import json
from pdf_processor import PDFProcessor

class FormMapper:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.forms_data = {}
        self.common_fields = self._define_common_fields()
        
    def _define_common_fields(self):
        """Define common real estate form fields"""
        return {
            'buyer_info': {
                'buyer_name': 'Buyer Full Name',
                'buyer_phone': 'Buyer Phone',
                'buyer_email': 'Buyer Email',
                'buyer_address': 'Buyer Address'
            },
            'seller_info': {
                'seller_name': 'Seller Full Name',
                'seller_phone': 'Seller Phone',
                'seller_email': 'Seller Email'
            },
            'property_info': {
                'property_address': 'Property Address',
                'apn': 'Assessor Parcel Number',
                'purchase_price': 'Purchase Price',
                'deposit_amount': 'Initial Deposit'
            },
            'agent_info': {
                'agent_name': 'Agent Name',
                'agent_license': 'Agent License Number',
                'brokerage': 'Brokerage Name',
                'agent_phone': 'Agent Phone'
            },
            'transaction_info': {
                'offer_date': 'Offer Date',
                'closing_date': 'Proposed Closing Date',
                'contingency_period': 'Contingency Period',
                'loan_type': 'Loan Type'
            }
        }
    
    def scan_pdf_forms(self):
        """Scan all PDF forms and map their fields"""
        pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            print(f"Analyzing {pdf_file}...")
            
            # Get fillable fields
            fields = self.pdf_processor.analyze_pdf_fields(pdf_file)
            
            # Get text structure for manual mapping
            structure = self.pdf_processor.extract_text_structure(pdf_file)
            
            self.forms_data[pdf_file] = {
                'fields': fields,
                'structure': structure,
                'mapped_fields': self._map_fields_to_common(fields, pdf_file)
            }
    
    def _map_fields_to_common(self, fields, filename):
        """Map PDF fields to common field names"""
        mapped = {}
        
        # This would contain intelligent mapping logic
        # For now, return the fields as-is
        return fields
    
    def get_all_forms(self):
        """Return all form data for frontend"""
        return {
            'forms': self.forms_data,
            'common_fields': self.common_fields
        }