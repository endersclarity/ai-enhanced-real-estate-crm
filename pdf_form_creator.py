#!/usr/bin/env python3
"""
PDF Form Creator - Build CAR forms from scratch with editable fields
Creates professional PDF forms that integrate with CRM system
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfform
import os

class PDFFormCreator:
    def __init__(self):
        self.width, self.height = letter
        self.margin = 0.75 * inch
        
    def create_california_purchase_agreement(self, output_path="california_purchase_agreement_editable.pdf"):
        """
        Create California Residential Purchase Agreement from scratch with editable fields
        """
        c = canvas.Canvas(output_path, pagesize=letter)
        
        # Header
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.margin, self.height - inch, "CALIFORNIA RESIDENTIAL PURCHASE AGREEMENT")
        c.drawString(self.margin, self.height - inch - 20, "AND JOINT ESCROW INSTRUCTIONS")
        
        # Form date
        c.setFont("Helvetica", 10)
        c.drawString(self.margin + 4*inch, self.height - inch - 40, "Date:")
        c.acroForm.textfield(
            name='form_date',
            tooltip='Date form was prepared',
            x=self.margin + 4.5*inch, y=self.height - inch - 55,
            borderStyle='inset',
            width=1.5*inch, height=15
        )
        
        # Property Information Section
        y_pos = self.height - 2*inch
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(self.margin, y_pos, "1. PROPERTY:")
        
        y_pos -= 30
        c.setFont("Helvetica", 10)
        c.drawString(self.margin, y_pos, "Property Address:")
        c.acroForm.textfield(
            name='property_address',
            tooltip='Full property address',
            x=self.margin + 1.2*inch, y=y_pos - 15,
            borderStyle='inset',
            width=4*inch, height=15
        )
        
        y_pos -= 50
        c.drawString(self.margin, y_pos, "City:")
        c.acroForm.textfield(
            name='property_city',
            tooltip='Property city',
            x=self.margin + 0.5*inch, y=y_pos - 15,
            borderStyle='inset',
            width=1.5*inch, height=15
        )
        
        c.drawString(self.margin + 2.2*inch, y_pos, "State:")
        c.acroForm.textfield(
            name='property_state',
            tooltip='Property state',
            x=self.margin + 2.7*inch, y=y_pos - 15,
            borderStyle='inset',
            width=0.5*inch, height=15
        )
        
        c.drawString(self.margin + 3.5*inch, y_pos, "Zip:")
        c.acroForm.textfield(
            name='property_zip',
            tooltip='Property ZIP code',
            x=self.margin + 3.8*inch, y=y_pos - 15,
            borderStyle='inset',
            width=1*inch, height=15
        )
        
        # Purchase Price Section
        y_pos -= 80
        c.setFont("Helvetica-Bold", 12)
        c.drawString(self.margin, y_pos, "2. PURCHASE PRICE:")
        
        y_pos -= 30
        c.setFont("Helvetica", 10)
        c.drawString(self.margin, y_pos, "The total purchase price is $")
        c.acroForm.textfield(
            name='purchase_price',
            tooltip='Total purchase price',
            x=self.margin + 1.8*inch, y=y_pos - 15,
            borderStyle='inset',
            width=1.5*inch, height=15
        )
        
        # Buyer Information Section
        y_pos -= 80
        c.setFont("Helvetica-Bold", 12)
        c.drawString(self.margin, y_pos, "3. BUYER(S):")
        
        y_pos -= 30
        c.setFont("Helvetica", 10)
        c.drawString(self.margin, y_pos, "Buyer Name:")
        c.acroForm.textfield(
            name='buyer_name',
            tooltip='Primary buyer full name',
            x=self.margin + 1*inch, y=y_pos - 15,
            borderStyle='inset',
            width=2.5*inch, height=15
        )
        
        y_pos -= 30
        c.drawString(self.margin, y_pos, "Phone:")
        c.acroForm.textfield(
            name='buyer_phone',
            tooltip='Buyer phone number',
            x=self.margin + 0.6*inch, y=y_pos - 15,
            borderStyle='inset',
            width=1.5*inch, height=15
        )
        
        c.drawString(self.margin + 2.5*inch, y_pos, "Email:")
        c.acroForm.textfield(
            name='buyer_email',
            tooltip='Buyer email address',
            x=self.margin + 2.9*inch, y=y_pos - 15,
            borderStyle='inset',
            width=2*inch, height=15
        )
        
        # Seller Information Section
        y_pos -= 80
        c.setFont("Helvetica-Bold", 12)
        c.drawString(self.margin, y_pos, "4. SELLER(S):")
        
        y_pos -= 30
        c.setFont("Helvetica", 10)
        c.drawString(self.margin, y_pos, "Seller Name:")
        c.acroForm.textfield(
            name='seller_name',
            tooltip='Primary seller full name',
            x=self.margin + 1*inch, y=y_pos - 15,
            borderStyle='inset',
            width=2.5*inch, height=15
        )
        
        y_pos -= 30
        c.drawString(self.margin, y_pos, "Phone:")
        c.acroForm.textfield(
            name='seller_phone',
            tooltip='Seller phone number',
            x=self.margin + 0.6*inch, y=y_pos - 15,
            borderStyle='inset',
            width=1.5*inch, height=15
        )
        
        c.drawString(self.margin + 2.5*inch, y_pos, "Email:")
        c.acroForm.textfield(
            name='seller_email',
            tooltip='Seller email address',
            x=self.margin + 2.9*inch, y=y_pos - 15,
            borderStyle='inset',
            width=2*inch, height=15
        )
        
        # Agent Information Section
        y_pos -= 80
        c.setFont("Helvetica-Bold", 12)
        c.drawString(self.margin, y_pos, "5. LISTING AGENT:")
        
        y_pos -= 30
        c.setFont("Helvetica", 10)
        c.drawString(self.margin, y_pos, "Agent Name:")
        c.acroForm.textfield(
            name='listing_agent_name',
            tooltip='Listing agent full name',
            x=self.margin + 1*inch, y=y_pos - 15,
            borderStyle='inset',
            width=2*inch, height=15
        )
        
        c.drawString(self.margin + 3.2*inch, y_pos, "License #:")
        c.acroForm.textfield(
            name='listing_agent_license',
            tooltip='Agent license number',
            x=self.margin + 3.9*inch, y=y_pos - 15,
            borderStyle='inset',
            width=1.2*inch, height=15
        )
        
        y_pos -= 30
        c.drawString(self.margin, y_pos, "Brokerage:")
        c.acroForm.textfield(
            name='listing_brokerage',
            tooltip='Listing brokerage name',
            x=self.margin + 0.8*inch, y=y_pos - 15,
            borderStyle='inset',
            width=2.5*inch, height=15
        )
        
        # Terms and Conditions Section
        y_pos -= 80
        c.setFont("Helvetica-Bold", 12)
        c.drawString(self.margin, y_pos, "6. TERMS AND CONDITIONS:")
        
        y_pos -= 30
        c.setFont("Helvetica", 10)
        c.drawString(self.margin, y_pos, "Closing Date:")
        c.acroForm.textfield(
            name='closing_date',
            tooltip='Expected closing date',
            x=self.margin + 1*inch, y=y_pos - 15,
            borderStyle='inset',
            width=1.5*inch, height=15
        )
        
        c.drawString(self.margin + 2.8*inch, y_pos, "Possession Date:")
        c.acroForm.textfield(
            name='possession_date',
            tooltip='Possession transfer date',
            x=self.margin + 3.9*inch, y=y_pos - 15,
            borderStyle='inset',
            width=1.5*inch, height=15
        )
        
        # Financing Section
        y_pos -= 50
        c.drawString(self.margin, y_pos, "Financing Type:")
        c.acroForm.textfield(
            name='financing_type',
            tooltip='Type of financing (Cash, Conventional, FHA, etc.)',
            x=self.margin + 1.2*inch, y=y_pos - 15,
            borderStyle='inset',
            width=2*inch, height=15
        )
        
        # Earnest Money
        y_pos -= 30
        c.drawString(self.margin, y_pos, "Earnest Money: $")
        c.acroForm.textfield(
            name='earnest_money',
            tooltip='Earnest money deposit amount',
            x=self.margin + 1.2*inch, y=y_pos - 15,
            borderStyle='inset',
            width=1*inch, height=15
        )
        
        # Contingencies Section
        y_pos -= 50
        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.margin, y_pos, "Contingencies:")
        
        y_pos -= 25
        c.setFont("Helvetica", 10)
        
        # Inspection Contingency Checkbox
        c.acroForm.checkbox(
            name='inspection_contingency',
            tooltip='Inspection contingency included',
            x=self.margin, y=y_pos - 10,
            size=10
        )
        c.drawString(self.margin + 15, y_pos, "Inspection Contingency")
        
        # Loan Contingency Checkbox  
        c.acroForm.checkbox(
            name='loan_contingency',
            tooltip='Loan contingency included',
            x=self.margin + 2*inch, y=y_pos - 10,
            size=10
        )
        c.drawString(self.margin + 2*inch + 15, y_pos, "Loan Contingency")
        
        # Appraisal Contingency Checkbox
        c.acroForm.checkbox(
            name='appraisal_contingency',
            tooltip='Appraisal contingency included',
            x=self.margin + 3.5*inch, y=y_pos - 10,
            size=10
        )
        c.drawString(self.margin + 3.5*inch + 15, y_pos, "Appraisal Contingency")
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(self.margin, 1*inch, "Page 1 of 1")
        c.drawString(self.margin, 0.7*inch, "Generated by Real Estate CRM System")
        
        c.save()
        return output_path
    
    def get_form_field_mapping(self):
        """
        Return mapping of form field names to CRM database columns
        """
        return {
            'form_date': 'transaction_date',
            'property_address': 'street_address',
            'property_city': 'city',
            'property_state': 'state',
            'property_zip': 'zip_code',
            'purchase_price': 'purchase_price',
            'buyer_name': 'buyer_name',
            'buyer_phone': 'buyer_phone',
            'buyer_email': 'buyer_email',
            'seller_name': 'seller_name',
            'seller_phone': 'seller_phone',
            'seller_email': 'seller_email',
            'listing_agent_name': 'listing_agent_name',
            'listing_agent_license': 'listing_agent_license',
            'listing_brokerage': 'listing_brokerage',
            'closing_date': 'closing_date',
            'possession_date': 'possession_date',
            'financing_type': 'financing_type',
            'earnest_money': 'earnest_money_amount',
            'inspection_contingency': 'inspection_contingency',
            'loan_contingency': 'loan_contingency',
            'appraisal_contingency': 'appraisal_contingency'
        }

def main():
    """Test the PDF form creator"""
    creator = PDFFormCreator()
    output_file = creator.create_california_purchase_agreement()
    print(f"Created editable PDF form: {output_file}")
    print("Form field mapping:", creator.get_form_field_mapping())

if __name__ == "__main__":
    main()